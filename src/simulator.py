import nibabel as nib
import numpy as np
import imageio
import random
import os
import scipy.ndimage as ndi
import matplotlib.pyplot as plt

class NIfTISimulator:
    """
    A class to simulate common issues in 3D NIfTI files, such as missing slides,
    incorrect sequences, and mixed axis simulations along a user-specified axis.
    """

    def __init__(self, file_path):
        """Initialize the simulator by loading a NIfTI file."""
        self.nifti_img = nib.load(file_path)
        self.original_data = self.nifti_img.get_fdata()
        self.original_shape = self.original_data.shape

    def clear_state(self):
        """Reset the simulator state to the original data."""
        pass  # No persistent state to clear in this implementation

    def simulate_missing_slides(self, data, remove_param, axis=0):
        num_slices = data.shape[axis]
        if isinstance(remove_param, int):
            k = remove_param
        elif isinstance(remove_param, float) and 0 <= remove_param <= 1:
            k = int(remove_param * num_slices)
        else:
            raise ValueError("remove_param must be an integer or float between 0 and 1")

        if k >= num_slices:
            raise ValueError("Cannot remove all or more slides than available along the axis")

        remove_indices = np.random.choice(num_slices, size=k, replace=False)
        simulated_data = np.delete(data, remove_indices, axis=axis)

        simulation_info = {
            'type': 'missing_slides',
            'remove_indices': remove_indices
        }
        return simulated_data, simulation_info

    def simulate_wrong_sequence(self, data, shuffle_param=None, axis=0):
        num_slices = data.shape[axis]
        if shuffle_param is None:
            shuffled_indices = np.random.permutation(num_slices)
        else:
            if isinstance(shuffle_param, int):
                m = shuffle_param
            elif isinstance(shuffle_param, float) and 0 <= shuffle_param <= 1:
                m = int(shuffle_param * num_slices)
            else:
                raise ValueError("shuffle_param must be an integer, float between 0 and 1, or None")

            if m > num_slices:
                raise ValueError("Cannot shuffle more slides than available along the axis")

            shuffle_indices = np.random.choice(num_slices, size=m, replace=False)
            shuffled_indices = np.arange(num_slices)
            shuffled_subset = np.random.permutation(shuffle_indices)
            shuffled_indices[shuffle_indices] = shuffled_subset

        simulated_data = np.take(data, shuffled_indices, axis=axis)

        simulation_info = {
            'type': 'wrong_sequence',
            'shuffled_indices': shuffled_indices
        }
        return simulated_data, simulation_info

    def simulate_mixed_axis(self, data, axis_list, weight_param):
        if not isinstance(axis_list, list) or len(axis_list) < 1 or len(axis_list) > 3:
            raise ValueError("axis_list must be a list of 1 to 3 integers between 0 and 2")
        axis_list = list(set(axis_list))
        if any(a not in [0, 1, 2] for a in axis_list):
            raise ValueError("axis_list must contain integers 0, 1, or 2")

        main_axis = axis_list[0]
        aux_axes = axis_list[1:] if len(axis_list) > 1 else []
        num_slices = data.shape[main_axis]

        if isinstance(weight_param, int):
            num_replace = weight_param
        elif isinstance(weight_param, float) and 0 <= weight_param <= 1:
            num_replace = int(weight_param * num_slices)
        else:
            raise ValueError("weight_param must be an integer or float between 0 and 1")
        if num_replace > num_slices:
            raise ValueError("Cannot replace more slides than available")

        replace_indices = np.random.choice(num_slices, size=num_replace, replace=False)
        simulated_data = data.copy()
        axis_source = np.full(num_slices, main_axis)

        for i in replace_indices:
            if aux_axes:
                aux_axis = np.random.choice(aux_axes)
                j = np.random.randint(self.original_data.shape[aux_axis])
                if aux_axis == 0:
                    slice_data = self.original_data[j, :, :]
                elif aux_axis == 1:
                    slice_data = self.original_data[:, j, :]
                elif aux_axis == 2:
                    slice_data = self.original_data[:, :, j]

                if main_axis == 0:
                    target_shape = data.shape[1:]
                elif main_axis == 1:
                    target_shape = (data.shape[0], data.shape[2])
                elif main_axis == 2:
                    target_shape = data.shape[:2]

                if aux_axis == 0:
                    source_shape = self.original_data.shape[1:]
                elif aux_axis == 1:
                    source_shape = (self.original_data.shape[0], self.original_data.shape[2])
                elif aux_axis == 2:
                    source_shape = self.original_data.shape[:2]

                zoom_factors = (target_shape[0] / source_shape[0], target_shape[1] / source_shape[1])
                resized_slice = ndi.zoom(slice_data, zoom_factors, order=1)

                if main_axis == 0:
                    simulated_data[i, :, :] = resized_slice
                elif main_axis == 1:
                    simulated_data[:, i, :] = resized_slice
                elif main_axis == 2:
                    simulated_data[:, :, i] = resized_slice

                axis_source[i] = aux_axis

        simulation_info = {
            'type': 'mixed_axis',
            'axis_source': axis_source,
            'mixed_positions': replace_indices
        }
        return simulated_data, simulation_info

    def simulate(self, simulations, chain=False, mode="independent", save_type=None, output_path=None):
        if isinstance(simulations, dict):
            simulations = [simulations]
        elif not isinstance(simulations, list):
            raise ValueError("simulations must be a dict or list of dicts")

        if mode in ["independent", "chained"] and len(simulations) < 2:
            raise ValueError(f"{mode.capitalize()} mode requires at least 2 simulation types")
        elif mode == "single" and len(simulations) != 1:
            raise ValueError("Single mode requires exactly 1 simulation type")

        if mode == "single":
            sim = simulations[0]
            sim_type = sim['type']
            
            if sim_type in ['missing_slides', 'wrong_sequence']:
                axis = sim['axis']
            else:
                axis = sim['axis_list'][0]
                print(sim['axis_list'][0])
              
                
            if sim_type == 'missing_slides':
                remove_param = sim['remove_param']
                simulated_data, sim_info = self.simulate_missing_slides(self.original_data, remove_param, axis)
                targets = {
                    'is_missing': 1 if len(sim_info['remove_indices']) > 0 else 0,
                    'missing_positions': sim_info['remove_indices'],
                    'presence_target': np.ones(self.original_shape[axis], dtype=int),
                    'sequence_target': np.setdiff1d(np.arange(self.original_shape[axis]), sim_info['remove_indices'])
                }
                targets['presence_target'][sim_info['remove_indices']] = 0
            elif sim_type == 'wrong_sequence':
                shuffle_param = sim['shuffle_param']
                simulated_data, sim_info = self.simulate_wrong_sequence(self.original_data, shuffle_param, axis)
                targets = {
                    'is_missing': 0,
                    'missing_positions': np.array([]),
                    'presence_target': np.ones(self.original_shape[axis], dtype=int),
                    'sequence_target': np.argsort(sim_info['shuffled_indices'])
                }
            elif sim_type == 'mixed_axis':
                axis_list = sim['axis_list']
                weight_param = sim['weight_param']
                simulated_data, sim_info = self.simulate_mixed_axis(self.original_data, axis_list, weight_param)
                targets = {
                    'is_mixed': 1 if len(sim_info['mixed_positions']) > 0 else 0,
                    'mixed_positions': sim_info['mixed_positions'],
                    'axis_source': sim_info['axis_source'],
                    'sequence_target': np.arange(self.original_shape[axis])
                }
            else:
                raise ValueError(f"Unknown simulation type: {sim_type}")

            if save_type and output_path:
                self.save_data(simulated_data, save_type, axis, output_path)
            return simulated_data, targets

        elif mode == "chained":
            current_data = self.original_data.copy()
            sim = simulations[0]
            sim_type = sim['type']
            if sim_type in ['missing_slides', 'wrong_sequence']:
                axis = simulations[0]['axis']
                N = self.original_shape[axis]
                final_to_original = np.arange(N)
                source_axis = np.full(N, axis)
            else:
                axis = simulations[0]['axis_list'][0]
                N = self.original_shape['axis_list'][0]
                final_to_original = np.arange(N)
                source_axis = np.full(N, axis)
                
            
            
            
            sim_types_applied = []

            for sim in simulations:
                sim_type = sim['type']
                sim_types_applied.append(sim_type)
                if sim_type == 'missing_slides':
                    remove_param = sim['remove_param']
                    axis = sim['axis']
                    current_data, sim_info = self.simulate_missing_slides(current_data, remove_param, axis)
                    final_to_original = np.delete(final_to_original, sim_info['remove_indices'])
                    source_axis = np.delete(source_axis, sim_info['remove_indices'])
                elif sim_type == 'wrong_sequence':
                    shuffle_param = sim['shuffle_param']
                    axis = sim['axis']
                    current_data, sim_info = self.simulate_wrong_sequence(current_data, shuffle_param, axis)
                    final_to_original = final_to_original[sim_info['shuffled_indices']]
                    source_axis = source_axis[sim_info['shuffled_indices']]
                elif sim_type == 'mixed_axis':
                    axis_list = sim['axis_list']
                    weight_param = sim['weight_param']
                    current_data, sim_info = self.simulate_mixed_axis(current_data, axis_list, weight_param)
                    source_axis = sim_info['axis_source']
                else:
                    raise ValueError(f"Unknown simulation type: {sim_type}")

            all_original = np.arange(N)
            targets = {
                'final_to_original': final_to_original,
                'source_axis': source_axis,
            }
            if 'missing_slides' in sim_types_applied:
                targets['missing_original_indices'] = np.setdiff1d(all_original, final_to_original)
                targets['presence_target'] = np.isin(all_original, final_to_original).astype(int)
            else:
                targets['missing_original_indices'] = np.array([])
                targets['presence_target'] = np.ones(N, dtype=int)
            targets['sequence_target'] = np.argsort(final_to_original) if len(final_to_original) > 0 else np.arange(N)
            targets['mixed_positions'] = np.where(source_axis != axis)[0] if 'mixed_axis' in sim_types_applied else np.array([])

            if save_type and output_path:
                self.save_data(current_data, save_type, axis, output_path)
            return current_data, targets

        else:  # mode == "independent"
            results = []
            for sim in simulations:
                sim_type = sim['type']
                if sim_type in ['missing_slides', 'wrong_sequence']:
                    axis = sim['axis']
                else:
                    axis = sim['axis_list'][0]
                    
                #axis = sim['axis']
                if sim_type == 'missing_slides':
                    remove_param = sim['remove_param']
                    simulated_data, sim_info = self.simulate_missing_slides(self.original_data, remove_param, axis)
                    targets = {
                        'is_missing': 1 if len(sim_info['remove_indices']) > 0 else 0,
                        'missing_positions': sim_info['remove_indices'],
                        'presence_target': np.ones(self.original_shape[axis], dtype=int),
                        'sequence_target': np.setdiff1d(np.arange(self.original_shape[axis]), sim_info['remove_indices'])
                    }
                    targets['presence_target'][sim_info['remove_indices']] = 0
                elif sim_type == 'wrong_sequence':
                    shuffle_param = sim['shuffle_param']
                    simulated_data, sim_info = self.simulate_wrong_sequence(self.original_data, shuffle_param, axis)
                    targets = {
                        'is_missing': 0,
                        'missing_positions': np.array([]),
                        'presence_target': np.ones(self.original_shape[axis], dtype=int),
                        'sequence_target': np.argsort(sim_info['shuffled_indices'])
                    }
                elif sim_type == 'mixed_axis':
                    axis_list = sim['axis_list']
                    weight_param = sim['weight_param']
                    simulated_data, sim_info = self.simulate_mixed_axis(self.original_data, axis_list, weight_param)
                    targets = {
                        'is_mixed': 1 if len(sim_info['mixed_positions']) > 0 else 0,
                        'mixed_positions': sim_info['mixed_positions'],
                        'axis_source': sim_info['axis_source'],
                        'sequence_target': np.arange(self.original_shape[axis])
                    }
                else:
                    raise ValueError(f"Unknown simulation type: {sim_type}")

                if save_type and output_path:
                    sim_output_path = f"{output_path}_{sim_type}" if output_path else f"sim_{sim_type}"
                    if save_type == '3d':
                        sim_output_path += ".nii.gz"
                    self.save_data(simulated_data, save_type, axis, sim_output_path)
                results.append((simulated_data, targets))
            return results

    def save_data(self, data, save_type, axis, output_path=None):
        if save_type == 'jpeg':
            if output_path is None:
                raise ValueError("output_path must be specified for JPEG saving")
            os.makedirs(output_path, exist_ok=True)
            num_slices = data.shape[axis]
            
            import random
            num_slices_to_save = random.sample(range(num_slices), min(12, num_slices))
            # num_slices_to_save = min(12, num_slices)  # Save up to 12 slices
            
            # Adjust the grid size to 2 rows and 6 columns
            fig, axes = plt.subplots(2, 6, figsize=(18, 6))
            fig.suptitle('Missing Slides  --remove_param 30', fontsize=20) #'Mixed Axis - Mixed Axial Coronal and Sagittal planes'
            
            for i in range(num_slices):
                if axis == 0:
                    slice_data = data[i, :, :]
                elif axis == 1:
                    slice_data = data[:, i, :]
                elif axis == 2:
                    slice_data = data[:, :, i]
                min_val = slice_data.min()
                max_val = slice_data.max()
                if max_val > min_val:
                    normalized = (slice_data - min_val) / (max_val - min_val) * 255
                else:
                    normalized = np.zeros_like(slice_data)
                normalized = normalized.astype(np.uint8)
                rot_data = np.rot90(normalized, k=1)
                
                if i <= 11:
                    row = i // 6
                    col = i % 6
                    print(f"Processing slice {i}: row={row}, col={col}") 
                    axes[row, col].imshow(rot_data, cmap='gray')
                    axes[row, col].axis('off')
                #axes[row, col].set_title(f'Slice {i}')
                
                imageio.imwrite(os.path.join(output_path, f'slice_{i:03d}.jpg'), rot_data)
                
            plt.tight_layout()
            plt.subplots_adjust(top=0.9, wspace=0.01, hspace=0.01)
            plt.savefig(os.path.join(output_path, 'snippet.jpg'))
            plt.close()
                
            print(f"Saved {num_slices} JPEG slices to {output_path}")
        elif save_type == '3d':
            if output_path is None:
                raise ValueError("output_path must be specified for 3D saving")
            new_img = nib.Nifti1Image(data, self.nifti_img.affine)
            nib.save(new_img, output_path)
            print(f"Saved 3D NIfTI file to {output_path}")
        else:
            raise ValueError("Invalid save_type. Choose 'jpeg' or '3d'")