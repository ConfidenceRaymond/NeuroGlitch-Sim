import argparse
import os
import json
import numpy as np
from tqdm import tqdm 
from pathlib import Path
from simulator import ArtifactSimulator
from gif_visualizer import save_gif
from param import Opts


class RunCLI:
    def __init__(self):
        self.parser = self._create_parser()
        
        
    def int_or_float(self, value):
        try:
            return int(value)
        except ValueError:
            return float(value)
        
    def get_fixed_range(self):
        args = self.parser.parse_args()
        if args.fixed_range == 'range':
            opt = Opts()
            args = opt
        elif args.fixed_range == 'fixed':  # fixed
            args = args
        else:
            raise ValueError(f"fixed_range {args.fixed_range} is invalid, value must be 'fixed' or 'range'")
        return args
    
   
    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description="Simulate issues on multiple NIfTI files (single, independent, or chained), generate GIFs, and document in JSON."
        )
        
        parser.add_argument("--i", type=str, default="../Sample_Data/", required=False,  help="Directory with NIfTI files")
        parser.add_argument("--o", type=str, default="../outputs/", help="Directory for outputs and JSON if not specified")
        parser.add_argument("--gif_dir", type=str, default="../outputs/gifs/", help="Directory for GIFs")
        parser.add_argument("--json_file", type=str, default=None, help="JSON output file (default: <o>/analysis_results.json)")
        parser.add_argument("--sim_img", type=str, choices=["single_img", "multi_img"], default="single_img", required=False, help="Number simulation image (single_img: 1, multi_img: 2+)")
        parser.add_argument("--sim_mode", type=str, choices=["single", "independent", "chained"], default="single", required=False, help="Simulation mode (single: 1, independent/chained: 2+)")
        parser.add_argument("--sim_type", type=str, nargs="+", choices=["missing_slides", "wrong_sequence", "mixed_axis"], required=False, help="Simulation types")

        # Simulation-specific parameters
        parser.add_argument("--remove_param", type=self.int_or_float, default=5, help="Number/fraction of slides to remove (missing_slides), fraction must be less than 1")
        parser.add_argument("--shuffle_param", type=self.int_or_float, default=0.5, help="Number/fraction of slides to shuffle (wrong_sequence), fraction must be less than 1")
        parser.add_argument("--weight_param", type=self.int_or_float, default=0.3, help="Number/fraction of slides to mix (mixed_axis), fraction must be less than 1")
        parser.add_argument("--mixed_axis_list", type=int, nargs="+", default=[0, 1, 2], help="Axes for mixed_axis (e.g., 0 1 2)")

        parser.add_argument("--axis", type=int, choices=[0, 1, 2], default=0, help="Main axis for simulations")
        parser.add_argument("--clear_state", action="store_true", help="Clear simulator state before each file")
        parser.add_argument("--verbose", action="store_true", default=False, help="print out check points")
        parser.add_argument("--save_type", type=str, choices=["3d", "jpeg", "None"], default="None", help="Output save type")
        parser.add_argument("--fixed_range", type=str, choices=["fixed", "range"], default="range", required=True, help="fixed value for simualtion or provide range in param.py")
        return parser
    
    def SetUp(self, args):
        # Validate sim_type based on mode
        if args.sim_mode == "single" and len(args.sim_type) != 1:
            print("Error: Single mode requires exactly 1 simulation type")
            return
        elif args.sim_mode in ["independent", "chained"] and len(args.sim_type) < 2:
            print(f"Error: {args.sim_mode.capitalize()} mode requires at least 2 simulation types")
            return
        
         # Validate input file
        if args.sim_img == 'single_img':
            if not os.path.isfile(args.i) or not args.i.endswith(('.nii', '.nii.gz')):
                print(f"Error: {args.i} is not a valid NIfTI file")
            return
       
        # Validate mixed_axis_list if mixed_axis is used
        if "mixed_axis" in args.sim_type:
            print("args.mixed_axis_list",len(args.mixed_axis_list))
            if len(args.mixed_axis_list) == 1 or len(args.mixed_axis_list) > 3:
                print("Error: mixed_axis_list must contain 1 to 3 integers (0, 1, or 2)")
                return
            
        print(args.gif_dir)
        # Ensure directories exist
        Path(args.o).mkdir(exist_ok=True)
        Path(args.gif_dir).mkdir(exist_ok=True)
        
        return
        
    
        
    def np_encoder(self, obj):
        if isinstance(obj, np.int64):
            return int(obj)
        return obj


    def write_to_json(self, json_path, analysis_results):
        # Check if the file exists and read existing data
        if os.path.exists(json_path):
            with open(json_path, 'r') as f:
                try:
                    existing_data = json.load(f)
                except json.JSONDecodeError:
                    existing_data = []  # If file is empty or corrupted, initialize as empty list
        else:
            existing_data = []

        # Append new results to the existing data
        existing_data.append(self.np_encoder(analysis_results))

        # Write updated data back to file
        with open(json_path, 'w') as f:
            json.dump(self.np_encoder(existing_data), f) # Removed indent=4

        print(f"Analysis results saved to {json_path}")

        
    
    def get_SimType(self, args):
        # args = self.parser.parse_args()
        # Configure simulations based on sim_type
        sim_configs = {}
        if "missing_slides" in args.sim_type:
            sim_configs["missing_slides"] = {'type': 'missing_slides', 'remove_param': args.remove_param, 'axis': args.axis}
        if "wrong_sequence" in args.sim_type:
            sim_configs["wrong_sequence"] = {'type': 'wrong_sequence', 'shuffle_param': args.shuffle_param, 'axis': args.axis}
        if "mixed_axis" in args.sim_type:
            sim_configs["mixed_axis"] = {'type': 'mixed_axis', 'axis_list': args.mixed_axis_list, 'weight_param': args.weight_param}
    
        selected_sims = [sim_configs[sim_type] for sim_type in args.sim_type]
        
        return selected_sims
    
    def SimOps(self, simulator, base_name, args):

        selected_sims = self.get_SimType(args)
        
        analysis_results = None
        
        if args.sim_mode == "single":
            data, targets = simulator.simulate(selected_sims, mode="single")
            sim_type = args.sim_type[0]
            gif_name = os.path.join(args.gif_dir, f"{base_name}_{sim_type}") #../gifs args.gif_dir
            save_gif(data, gif_name, axis=args.axis)
        
            entry = {
                "file_name": base_name,
                "simulation_mode": "single",
                "simulation_type": sim_type,
                "parameters": {k: v for k, v in selected_sims[0].items() if k != 'type'},
                "targets": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in targets.items()},
                "output_shape": list(data.shape),
                "fixed_range": args.fixed_range
            }
            analysis_results = entry
        
            if args.save_type != "None":
                output_path = os.path.join(args.o, f"{base_name}_{sim_type}")
                if args.save_type == "3d":
                    output_path += ".nii.gz"
                simulator.save_data(data, args.save_type, args.axis, output_path)
                entry["output_path"] = output_path
                
            if args.verbose:
                print(f"Processed {sim_type}: Shape {data.shape}, GIF saved to {gif_name}")
    
        elif args.sim_mode == "independent":
            results = simulator.simulate(selected_sims, mode="independent")
            for (data, targets), sim in zip(results, selected_sims):
                sim_type = sim['type']
                gif_name = os.path.join(args.gif_dir, f"{base_name}_{sim_type}.gif")
                save_gif(data, gif_name, axis=args.axis)
            
                entry = {
                    "file_name": base_name,
                    "simulation_mode": "independent",
                    "simulation_type": sim_type,
                    "parameters": {k: v for k, v in sim.items() if k != 'type'},
                    "targets": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in targets.items()},
                    "output_shape": list(data.shape),
                    "fixed_range": args.fixed_range
                }
                analysis_results = entry
            
                if args.save_type != "None":
                    output_path = os.path.join(args.o, f"{base_name}_{sim_type}")
                    if args.save_type == "3d":
                        output_path += ".nii.gz"
                    simulator.save_data(data, args.save_type, args.axis, output_path)
                    entry["output_path"] = output_path
                    
                if args.verbose:
                    print(f"Processed {sim_type}: Shape {data.shape}, GIF saved to {gif_name}")
    
        else:  # Chained mode
            chained_data, chained_targets = simulator.simulate(selected_sims, mode="chained")
            chained_gif_name = os.path.join(args.gif_dir, f"{base_name}_chained_{'_'.join(args.sim_type)}.gif")
            save_gif(chained_data, chained_gif_name, axis=args.axis)
        
            chained_entry = {
                "file_name": base_name,
                "simulation_mode": "chained",
                "simulation_types": args.sim_type,
                "parameters": [{k: v for k, v in sim.items() if k != 'type'} for sim in selected_sims],
                "targets": {k: v.tolist() if isinstance(v, np.ndarray) else v for k, v in chained_targets.items()},
                "output_shape": list(chained_data.shape),
                "fixed_range": args.fixed_range
            }
            analysis_results = chained_entry
        
            if args.save_type != "None":
                chained_output_path = os.path.join(args.o, f"{base_name}_chained_{'_'.join(args.sim_type)}")
                if args.save_type == "3d":
                    chained_output_path += ".nii.gz"
                simulator.save_data(chained_data, args.save_type, args.axis, chained_output_path)
                chained_entry["output_path"] = chained_output_path
                
            if args.verbose:
                print(f"Processed chained ({', '.join(args.sim_type)}): Shape {chained_data.shape}, GIF saved to {chained_gif_name}")
            
        return analysis_results     
        
    
    def MultiFile(self, args):
        _ = self.SetUp(args)
        json_paths = os.path.join(args.o, "multi_analysis_results.json")  
        
        print(json_paths)
        
        # Get image paths
        nifti_files = [f for f in os.listdir(args.i) if f.endswith(('.nii', '.nii.gz'))]
        if not nifti_files:
            print(f"No NIfTI files found in {args.i}")
            return
    
        analysis_results = []
        # print(args.sim_type) 
        print('remove_param_arg', args.remove_param)
        
    
        for nifti_file in tqdm(nifti_files, desc="Simulating MRI files"):
            file_path = os.path.join(args.i, nifti_file)
            base_name = os.path.splitext(os.path.splitext(nifti_file)[0])[0]
            reset_args = self.get_fixed_range() #Re
            # print(reset_args.sim_type)
            print('remove_param_reset_args', reset_args.remove_param)

            simulator = ArtifactSimulator(file_path)
            if reset_args.clear_state:
                simulator.clear_state()
                
            if args.verbose:
                print(f"Processing {nifti_file} in {reset_args.sim_mode} mode with simulations: {reset_args.sim_type}...")
                
            multi_analysis_results = self.SimOps(simulator, base_name, reset_args)
            
            analysis_results.append(multi_analysis_results)
            
        self.write_to_json(json_paths, analysis_results)
            
    def SingleFile(self, args):
        _ = self.SetUp(args)
        
        
        file_path = args.i
        base_name = os.path.splitext(os.path.splitext(os.path.basename(file_path))[0])[0]
        json_name = f"{base_name}_{'_'.join(args.sim_type)}" if len(args.sim_type) >1 else f"{base_name}_{args.sim_type}.json"
        json_path = os.path.join(args.o, json_name) 
        
        
        print(f"Processing {file_path} in {args.sim_mode} mode with simulations: {args.sim_type}...")
        
        simulator = ArtifactSimulator(file_path)
        if args.clear_state:
            simulator.clear_state()
        
        analysis_results = []
        single_analysis_results = self.SimOps(simulator, base_name, args)
        analysis_results.append(single_analysis_results)
        
        self.write_to_json(json_path, analysis_results)
        
        
    def run(self):
        args = self.get_fixed_range()
        if args.sim_img == "single_img":
            self.SingleFile(args) # args
        elif args.sim_img == "multi_img":
            self.MultiFile(args) # args
        else:
            raise ValueError(f"Unknown simulation image type: {args.sim_img}")
        
        
if __name__ == "__main__":
    cli = RunCLI()
    cli.run()