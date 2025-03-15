

##  NifTI Simulation Visualization (NIftI-SimViz)
A Python tool for simulating `missing slides, wrong sequence, and mixed axis` issues in 3D NIfTI brain imaging data, either `single, independently or chained`, visualizing results as GIFs, and documenting simulation details in JSON. Supports batch processing of multiple files or single-file processing with customizable simulation types.

The `single mode` applies one simulation (e.g., missing_slides) to a NIfTI file, producing a single output with specific targets, ideal for isolated analysis. The `independent mode` applies multiple simulations (e.g., `missing_slides and wrong_sequence`) separately to the original data, generating distinct outputs and targets for each, allowing comparison of individual effects. The `chained mode` applies multiple simulations sequentially (e.g., `mixed_axis then wrong_sequence`), with each simulation modifying the previous result, producing a single output with combined targets like `final_to_original and source_axis`, reflecting the cumulative impact of ordered transformations.

###  Setup
```bash
git clone https://github.com/ConfidenceRaymond/NeuroGlitch.git
cd NeuroGlitch
pip install -r requirements.txt

```

###  Example Usage from Terminal
The `single mode` applies one simulation (e.g., missing_slides) to a NIfTI file, producing a single output with specific targets, ideal for isolated analysis.  The `chained mode` applies multiple simulations sequentially (e.g., `mixed_axis then wrong_sequence`), with each simulation modifying the previous result, producing a single output with combined targets like `final_to_original and source_axis`, reflecting the cumulative impact of ordered transformations. The `fixed_range`  parameter `range` option randomizes the simulation procces. It requires `upper and lower bounds` for each simulation parameter to be modified in the `param.py` file, while the `fixed` option allows you to provide your fixed parameters from the terminal.

**Missing Slides Simulation:**
- **Description:** `missing_slides` randomly removes a specified number or fraction of slices along a chosen axis, simulating data loss, with targets tracking removed positions and presence.
- **Command**:
  ```bash
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range range # randomize parameter
  or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --sim_mode single --sim_type missing_slides --sim_img single_img --remove_param 5 --axis 0
  or
  python NeuroGlitch.py -i Sample_Data/ --fixed_range fixed --sim_mode single --sim_type missing_slides --sim_img single_img --remove_param 5 --axis 0 # multiple data in a folder
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_missing_slides.nii.gz`, `outputs/MNI152_T1_2mm_brain_missing_slides.json` `outputs/gifs/MNI152_T1_2mm_brain_missing_slides.gif`
 ![Missing Slides Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet.jpg)


**Wrong Sequence Simulation:**
- **Description:** `wrong_sequence` randomly shuffles a specified number or fraction of slices along a chosen axis, simulating misordering, with targets providing the original sequence order. 
- **Command**:
  ```bash
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz  --fixed_range range
  or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --shuffle_param 0.3 --axis 1
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_wrong_sequence.nii.gz`, `outputs/MNI152_T1_2mm_brain_wrong_sequence.json` `outputs/gifs/MNI152_T1_2mm_brain_wrong_sequence.gif`
![Wrong Sequence Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet_ws.jpg)

**Mixed Axis Simulation:**
- **Description:** `mixed_axis`replaces a specified number or fraction of slices along a primary axis with data from auxiliary axes (resized if needed), simulating axis confusion, with targets identifying mixed positions and source axes. 
- **Command**:
  ```bash
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range range
   or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --weight_param 0.3 --mixed_axis_list 0 1
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_mixed_axis.nii.gz`, `outputs/MNI152_T1_2mm_brain_mixed_axis.json` `outputs/gifs/MNI152_T1_2mm_brain_mixed_axis.gif`
![Mixed Axis Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet_ma.jpg)

**Independent Mode Multiple Simulation:**
- **Description:** `independent` applies multiple simulations (e.g., `missing_slides and wrong_sequence`) separately to the original data, generating distinct outputs and targets for each, allowing comparison of individual effects. 
- **Command**:
  ```bash 
  cd src
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range range
   or
  python NeuroGlitch.py -i Sample_Data/MNI152_T1_2mm_brain.nii.gz --fixed_range fixed --weight_param 0.3 --mixed_axis_list 0 1
  ```
- **Output Files**: `outputs/MNI152_T1_2mm_brain_wrong_sequence.nii.gz`, `outputs/MNI152_T1_2mm_brain_wrong_sequence.json` `outputs/gifs/MNI152_T1_2mm_brain_wrong_sequence.gif`


##  CLI Parameters

* **`--input_dir`**: Directory containing NIfTI files or Directory to single nii or nii.gz file (default: `data/`)
* **`--output_dir`**: Directory for outputs and JSON (default: `outputs/`)
* **`--gif_dir`**: Directory for generated GIFs (default: `gifs/`)
* **`--json_file`**: Path to the JSON output file (default: `<output_dir>/analysis_results.json`)
* **`--sim_mode`**: Simulation mode: `single` or `independent` or `chained` (default: `independent`)
* **`--save_type`**: Output save type: `3d`, `jpeg`, or `None` (default: `None`)
* **`--sim_type`**: List of simulations to run (e.g., `missing_slides, wrong_sequence and mixed_axis` or a combination aon any in parallel or series) 
* **`--clear_state`**: Clears the simulator's internal state before running a simulation.

* **`--remove_param`**: Simulation parameter for removing elements, determines number of slides to be removed or percentage. Reguired for `missing_slides`
* **`--shuffle_param`**: Simulation parameter for shuffling elements, determines number of slides to be randomized or percentage. Reguired for `wrong_sequence`
* **`--axis`**: Main axis for processing (default: `0`; option: `0,1,2`) Reguired for `missing_slides` and `wrong_sequence`
* **`--weight_param`**: Simulation parameter for weighting elements. Reguired for `mixed_axis`
* **`--mixed_axis_list`**: List of axes for mixed-axis operations (default: `[0 1 2]`; option: `[0 1] or [0 1 2]`) Reguired for `mixed_axis`



##  Usage
**Single File Processing**

_Use single_file_cli.py for a single file_
_Single file, single mode:_

_Single file, independent mode:_
```bash
python src/single_file_cli.py --input_dir data/ --sim_mode independent --sim_type wrong_sequence mixed_axis --shuffle_param 0.7 --weight_param 0.4
```

_Single file, chain mode:_
```bash
python src/single_file_cli.py --input_file data/image1.nii.gz --sim_mode chained --sim_type mixed_axis wrong_sequence --weight_param 0.4 --shuffle_param 0.6
```

**Batch Processing (Multiple Files)**
_Use multi_file_cli.py for multiple files_
_Multiple file, single mode:_
```bash
python src/multi_file_cli.py --input_dir data/ --sim_mode single --sim_type wrong_sequence --shuffle_param 0.7
```

_Multiple Files, independent mode:_
```bash
python src/multi_file_cli.py --input_dir data/ --sim_mode independent --sim_type missing_slides mixed_axis --remove_param 8 --weight_param 0.4
```

_Multiple Files, Chained mode:_

## Installation
```bash
git clone https://github.com/ConfidenceRaymond/NIftI-SimViz.git
cd NIftI-SimViz
pip install -r requirements.txt
cd scr
```


**Output Locations**
* **Single Mode:** One GIF/output per simulation
    * GIFs: gifs/ (e.g., image1_missing_slides.gif)
    * Simulation Data: outputs/ (e.g., image1_missing_slides.nii.gz if 3d)
* **Independent Mode:** One GIF/output per simulation type
    * GIFs: gifs/ (e.g., image1_missing_slides.gif)
Simulation Data: outputs/ (e.g., image1_missing_slides.nii.gz if 3d)
* **Chained Mode:** One GIF/output combining selected simulations
    * GIFs: gifs/ (e.g., image1_chained.gif)
    * Simulation Data: outputs/ (e.g., image1_chained.nii.gz if 3d)
JSON Analysis: --json_file or <output_dir>/analysis_results.json
**JSON Output Format**
* **Single Mode:** One entry per simulation type
    * file_name, simulation_mode: "single", simulation_type, axis_list (for mixed_axis), targets, output_shape
* **Independent Mode:** One entry per simulation type
    * file_name, simulation_mode: "independent", simulation_type, axis_list (for mixed_axis), targets, output_shape
* **Chained Mode:** One entry with combined simulations
    * file_name, simulation_mode: "chained", simulation_types, axis_list (if mixed_axis included), targets, output_shape


**JSON Output Format**
**Independent:** Simulation entry
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

**Chained: One entry with ordered simulation types**
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