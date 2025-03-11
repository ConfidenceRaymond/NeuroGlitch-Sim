

A Python tool for simulating `missing slides, wrong sequence, and mixed axis` issues in 3D NIfTI brain imaging data, either `**single, independently or chained**`, visualizing results as GIFs, and documenting simulation details in JSON. Supports batch processing of multiple files or single-file processing with customizable simulation types.

The `**single mode**` applies one simulation (e.g., missing_slides) to a NIfTI file, producing a single output with specific targets, ideal for isolated analysis. The `**independent mode**` applies multiple simulations (e.g., `missing_slides and wrong_sequence`) separately to the original data, generating distinct outputs and targets for each, allowing comparison of individual effects. The `**chained mode**` applies multiple simulations sequentially (e.g., `mixed_axis then wrong_sequence`), with each simulation modifying the previous result, producing a single output with combined targets like `final_to_original and source_axis`, reflecting the cumulative impact of ordered transformations.

**Missing_slides:** Randomly removes a specified number or fraction of slices along a chosen axis, simulating data loss, with targets tracking removed positions and presence. ![Missing Slides Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet.jpg)

**wrong_sequence:** Randomly shuffles a specified number or fraction of slices along a chosen axis, simulating misordering, with targets providing the original sequence order. ![Wrong Sequence Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet_ws.jpg)

**Mixed_axis:** Replaces a specified number or fraction of slices along a primary axis with data from auxiliary axes (resized if needed), simulating axis confusion, with targets identifying mixed positions and source axes. ![Mixed Axis Example](https://github.com/ConfidenceRaymond/NIftI-SimViz/blob/main/Sample_Data/snippet_ma.jpg)




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
Use single_file_cli.py for a single file
Single file, single mode:

Single file, independent mode:
```bash
python src/single_file_cli.py --input_dir data/ --sim_mode independent --sim_type wrong_sequence mixed_axis --shuffle_param 0.7 --weight_param 0.4
```

Single file, chain mode:
```bash
python src/single_file_cli.py --input_file data/image1.nii.gz --sim_mode chained --sim_type mixed_axis wrong_sequence --weight_param 0.4 --shuffle_param 0.6
```

**Batch Processing (Multiple Files)**
Use multi_file_cli.py for multiple files
Multiple file, single mode:
```bash
python src/multi_file_cli.py --input_dir data/ --sim_mode single --sim_type wrong_sequence --shuffle_param 0.7
```

Multiple Files, independent mode:
```bash
python src/multi_file_cli.py --input_dir data/ --sim_mode independent --sim_type missing_slides mixed_axis --remove_param 8 --weight_param 0.4
```

Multiple Files, Chained mode:

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