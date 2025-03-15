

##  NifTI Simulation Visualization (NIftI-SimViz)
A Python tool for simulating `missing slides, wrong sequence, and mixed axis` issues in 3D NIfTI brain imaging data, either `single, independently or chained`, visualizing results as GIFs, and documenting simulation details in JSON. Supports batch processing of multiple files or single-file processing with customizable simulation types.

###  Setup
```bash
git clone https://github.com/ConfidenceRaymond/NeuroGlitch.git
cd NeuroGlitch
pip install -r requirements.txt

```

##  Example Usage from Terminal
The `fixed_range` parameter's `range` option randomizes the simulation process. It requires `upper and lower bounds` for each simulation parameter to be modified in the `param.py` file, while the `fixed` option allows you to provide your fixed parameters from the terminal.

### Single Image Mode
Combinining the `single mode` and `single_img` applies one simulation (e.g., `missing_slides`) to a single NIfTI file, producing a single output with specific targets, ideal for isolated analysis.   

**Missing Slides Simulation:**
- **Description:** `missing_slides` randomly removes a specified number or fraction of slices along a chosen axis, simulating data loss, with targets tracking removed positions and presence.
- **Command**:
  ```bash
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range range # randomize parameter
  or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --sim_mode single --sim_type missing_slides --sim_img single_img --save_type 3d --remove_param 5 --axis 0
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_missing_slides.nii.gz`, `outputs/MNI152_T1_2mm_brain_missing_slides.json`, `outputs/gifs/MNI152_T1_2mm_brain_missing_slides.gif`
 ![Missing Slides Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet.jpg)


**Wrong Sequence Simulation:**
- **Description:** `wrong_sequence` randomly shuffles a specified number or fraction of slices along a chosen axis, simulating misordering, with targets providing the original sequence order. 
- **Command**:
  ```bash
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz  --fixed_range range
  or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --sim_mode single --sim_type missing_slides --sim_img single_img --save_type 3d --shuffle_param 0.3 --axis 1
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_wrong_sequence.nii.gz`, `outputs/MNI152_T1_2mm_brain_wrong_sequence.json`, `outputs/gifs/MNI152_T1_2mm_brain_wrong_sequence.gif`
![Wrong Sequence Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet_ws.jpg)

**Mixed Axis Simulation:**
- **Description:** `mixed_axis`replaces a specified number or fraction of slices along a primary axis with data from auxiliary axes (resized if needed), simulating axis confusion, with targets identifying mixed positions and source axes. 
- **Command**:
  ```bash
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range range
   or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --sim_mode single --sim_type missing_slides --sim_img single_img --save_type 3d --weight_param 0.3 --mixed_axis_list 0 1
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_mixed_axis.nii.gz`, `outputs/MNI152_T1_2mm_brain_mixed_axis.json`, `outputs/gifs/MNI152_T1_2mm_brain_mixed_axis.gif`
![Mixed Axis Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet_ma.jpg)

**Independent Mode Multiple Simulation:**
- **Description:** `independent` applies multiple simulations (e.g., `wrong_sequence and mixed_axis`) separately to the original data, generating distinct outputs and targets for each, allowing comparison of individual effects. This mode requires a minimum of two simulations.
- **Command**:
  ```bash 
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range range
   or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --sim_mode independent --sim_type wrong_sequence mixed_axis --sim_img single_img --save_type 3d --weight_param 0.3 --mixed_axis_list 0 1 --shuffle_param 0.3 --axis 0
  ```
- **Output Files**: For `wrong_sequence`: `outputs/MNI152_T1_2mm_brain_wrong_sequence.nii.gz`, `outputs/MNI152_T1_2mm_brain_wrong_sequence.json`, `outputs/gifs/MNI152_T1_2mm_brain_wrong_sequence.gif`. For `mixed_axis`: `outputs/MNI152_T1_2mm_brain_mixed_axis.nii.gz`, `outputs/MNI152_T1_2mm_brain_mixed_axis.json`, `outputs/gifs/MNI152_T1_2mm_brain_mixed_axis.gif`


**Chained Mode Multiple Simulation:**
- **Description:** `chained` applies multiple simulations sequentially (e.g., `wrong_sequence then mixed_axis`), with each simulation modifying the previous result, producing a single output with combined targets like `final_to_original and source_axis`, reflecting the cumulative impact of ordered transformations.. This mode requires a minimum of two simulations. _In `chained mode` when applying `mixed_axis` before of after other simulation types ensure the `--axis` value is the same as the the first axis of the `--mixed_axis_list` e.g., `axis = 1 and mixed_axis_list 1 0 2`.This authomatically taken care of in `range` randomized option_
- **Command**:
  ```bash 
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range range
   or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --sim_mode chained --sim_type wrong_sequence mixed_axis --sim_img single_img --save_type 3d --weight_param 0.3 --mixed_axis_list 0 1 --shuffle_param 0.3 --axis 0
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_wrong_sequence_mixed_axis.nii.gz`, `outputs/multi_analysis_results.json`, `outputs/gifs/MNI152_T1_2mm_brain_wrong_sequence.gif`, `outputs/gifs/MNI152_T1_2mm_brain_mixed_axis.gif`

### Multiple Image Mode
Combinining the `single mode` and `multi_img` applies one simulation (e.g., `missing_slides`) to a multiple NIfTI file, producing a single output with specific targets, ideal for isolated analysis.  

**Multiple Files Simulation:**
- **Description:** `multi_img` take a path to a folder loads all `.nii and .nii.gz` files and applies single or multiple simulations, producing a single output or multiple outputs depending on the `simulation mode`.  
- **Command**:
  ```bash
  cd src
  python NeuroGlitch.py -i Sample_Data/ --fixed_range range # randomize parameter
  or
  python NeuroGlitch.py -i Sample_Data/ --fixed_range fixed --sim_mode single --sim_type missing_slides --sim_img multi_img --save_type 3d --remove_param 5 --axis 0
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_missing_slides.nii.gz`, `outputs/MNI152_T1_2mm_brain_1_missing_slides.nii.gz` `outputs/MNI152_T1_2mm_brain_2_missing_slides.nii.gz`, , `outputs/gifs/MNI152_T1_2mm_brain_missing_slides.gif`, , `outputs/gifs/MNI152_T1_2mm_brain_1_missing_slides.gif`, , `outputs/gifs/MNI152_T1_2mm_brain_2_missing_slides.gif`, `outputs/MNI152_T1_2mm_brain_missing_slides.json`



##  CLI Parameters

* **`--i`**: Directory containing NIfTI files or Directory to single nii or nii.gz file (default: `data/`)
* **`--o`**: Directory for outputs and JSON (default: `outputs/`)
* **`--gif_dir`**: Directory for generated GIFs (default: `gifs/`)
* **`--json_file`**: Path to the JSON output file (default: `<output_dir>/analysis_results.json`)
* **`--sim_mode`**: Simulation mode: `single` or `independent` or `chained` (default: `independent`)
* **`--sim_type`**: List of simulations to run (e.g., `missing_slides, wrong_sequence and mixed_axis` or a combination aon any in parallel or series) 
* **`--sim_img`**: Number of simulation image (`single_img`: 1, `multi_img`: 2+) (e.g., `single_img, multi_img`) 
* **`--fixed_range`**: Randomized of fixed (`fixed`: provide fixed parameter in terminal, `range`: provide parameter `upper and lower bound` in `param.py`)  (e.g., `fixed, range`) 
* **`--save_type`**: Output save type: `3d`, `jpeg`, or `None` (default: `None`) `3d` save image as NIftI, `jpeg` save image as jpeg, `None` dont save images.
* **`--clear_state`**: Clears the simulator's internal state before running a simulation.
* **`--remove_param`**: Simulation parameter for removing elements, determines number of slides(_must be an integer_) to be removed or percentage(_must be an float less than 1_). Reguired for `missing_slides`
* **`--shuffle_param`**: Simulation parameter for shuffling elements, determines number of slides(_must be an integer_) to be randomized or percentage(_must be an float less than 1_). Reguired for `wrong_sequence`
* **`--weight_param`**: Simulation parameter for weighting elements, determines number of slides(_must be an integer_) to be mixed or percentage(_must be an float less than 1_). Reguired for `mixed_axis`
* **`--mixed_axis_list`**: List of axes for mixed-axis operations (default: `[0 1 2]`; option: `['0,1', '0,2', '1,0', '2,0', '1,2', '2,1', '0,1,2', '0,2,1', '1,0,2', '1,2,0', '2,0,1', '2,1,0'] `) Reguired for `mixed_axis`
* **`--axis`**: Main axis for processing (default: 0; options: 0 or 1 or 2) Reguired for `missing_slides` and `wrong_sequence`
* **`--verbose`**: Main axis for processing (default: Flase; options: True or False). Print out check points


**JSON Output Format**
**Single:** Simulation entry
```json
[
    {
        "file_name": "image1",
        "simulation_mode": "single",
        "simulation_type": "missing_slides",
        "parameters": {"remove_param": 10, "axis": 0},
        "targets": {"is_missing": 1, "missing_positions": [1, 3], "presence_target": [1, 0, 1, ...], "sequence_target": [0, 2, ...]},
        "output_shape": [89, 91, 109],
        "gif_path": "gifs/image1_missing_slides.gif"
    }
]
```

**Independent:** One entry per simulation
```json
[
    {
        "file_name": "image1",
        "simulation_mode": "independent",
        "simulation_type": "missing_slides",
        "parameters": {"remove_param": 10, "axis": 0},
        "targets": {"is_missing": 1, "missing_positions": [1, 3, 5], "presence_target": [1, 0, 1, ...], "sequence_target": [0, 2, 4, ...]},
        "output_shape": [81, 91, 109],
        "gif_path": "gifs/image1_missing_slides.gif",
        "output_path": "outputs/image1_missing_slides.nii.gz"
    }
]
```

**Chained:** One entry with ordered simulation types
```json
[
    {
        "file_name": "image1",
        "simulation_mode": "chained",
        "simulation_types": ["mixed_axis", "wrong_sequence"],
        "parameters": [
            {"axis_list": [0, 1, 2], "weight_param": 0.4},
            {"shuffle_param": 0.6, "axis": 0}
        ],
        "targets": {
            "final_to_original": [2, 0, 1, ...],
            "source_axis": [1, 0, 2, ...],
            "missing_original_indices": [],
            "presence_target": [1, 1, 1, ...],
            "sequence_target": [1, 2, 0, ...],
            "mixed_positions": [0, 2, 5, ...]
        },
        "output_shape": [91, 91, 109],
        "gif_path": "gifs/image1_chained_mixed_axis_wrong_sequence.gif",
        "output_path": "outputs/image1_chained_mixed_axis_wrong_sequence.nii.gz"
    }
]
```