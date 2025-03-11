import argparse
import os
import json
import numpy as np
from pathlib import Path
from simulator import NIfTISimulator
from gif_visualizer import save_gif

class NIfTI_SingleFileCLI:
    def __init__(self):
        self.parser = self._create_parser()
   
    def _create_parser(self):
        parser = argparse.ArgumentParser(
            description="Simulate issues on a single NIfTI file (single, independent, or chained), generate GIFs, and document in JSON."
        )
        parser.add_argument("--input_file", type=str, required=True, help="Path to the input NIfTI file (.nii or .nii.gz)")
        parser.add_argument("--output_dir", type=str, default="../outputs/", help="Directory to save outputs and JSON if not specified")
        parser.add_argument("--gif_dir", type=str, default="../outputs/gifs/", help="Directory to save GIFs")
        parser.add_argument("--json_file", type=str, default=None, help="JSON output file (default: <output_dir>/analysis_results.json)")
        parser.add_argument("--sim_mode", type=str, choices=["single", "independent", "chained"], default="single", help="Simulation mode (single: 1, independent/chained: 2+)")
        parser.add_argument("--sim_type", type=str, nargs="+", choices=["missing_slides", "wrong_sequence", "mixed_axis"], required=True, help="Simulation types")

        # Simulation-specific parameters
        parser.add_argument("--remove_param", type=int, default=5, help="Number/fraction of slides to remove (missing_slides)")
        parser.add_argument("--shuffle_param", type=float, default=0.5, help="Number/fraction of slides to shuffle (wrong_sequence)")
        parser.add_argument("--weight_param", type=float, default=0.3, help="Number/fraction of slides to mix (mixed_axis)")
        parser.add_argument("--mixed_axis_list", type=int, nargs="+", default=[0, 1, 2], help="Axes for mixed_axis (e.g., 0 1 2)") #nargs="+",

        parser.add_argument("--axis", type=int, choices=[0, 1, 2], default=0, help="Main axis for simulations")
        parser.add_argument("--clear_state", action="store_true", help="Clear simulator state before running")
        parser.add_argument("--save_type", type=str, choices=["3d", "jpeg", "None"], default="None", help="Output save type")
        return parser

    def run(self):
        args = self.parser.parse_args()
        print(args.mixed_axis_list)
       
        # Validate sim_type based on mode
        if args.sim_mode == "single" and len(args.sim_type) != 1:
            print("Error: Single mode requires exactly 1 simulation type")
            return
        elif args.sim_mode in ["independent", "chained"] and len(args.sim_type) < 2:
            print(f"Error: {args.sim_mode.capitalize()} mode requires at least 2 simulation types")
            return
       
        # Validate input file
        if not os.path.isfile(args.input_file) or not args.input_file.endswith(('.nii', '.nii.gz')):
            print(f"Error: {args.input_file} is not a valid NIfTI file")
            return
       
        # Validate mixed_axis_list if mixed_axis is used
        if "mixed_axis" in args.sim_type:
            print("args.mixed_axis_list",len(args.mixed_axis_list))
            if len(args.mixed_axis_list) == 1 or len(args.mixed_axis_list) > 3:
                print("Error: mixed_axis_list must contain 1 to 3 integers (0, 1, or 2)")
                return
       
        # Ensure directories exist
        Path(args.output_dir).mkdir(exist_ok=True)
        Path(args.gif_dir).mkdir(exist_ok=True)
        json_path = args.json_file if args.json_file else os.path.join(args.output_dir, "analysis_results.json")
       
        # Configure simulations based on sim_type
        sim_configs = {}
        if "missing_slides" in args.sim_type:
            sim_configs["missing_slides"] = {'type': 'missing_slides', 'remove_param': args.remove_param, 'axis': args.axis}
        if "wrong_sequence" in args.sim_type:
            sim_configs["wrong_sequence"] = {'type': 'wrong_sequence', 'shuffle_param': args.shuffle_param, 'axis': args.axis}
        if "mixed_axis" in args.sim_type:
            sim_configs["mixed_axis"] = {'type': 'mixed_axis', 'axis_list': args.mixed_axis_list, 'weight_param': args.weight_param}
       
        selected_sims = [sim_configs[sim_type] for sim_type in args.sim_type]

        file_path = args.input_file
        base_name = os.path.splitext(os.path.splitext(os.path.basename(file_path))[0])[0]
        print(f"Processing {file_path} in {args.sim_mode} mode with simulations: {args.sim_type}...")
       
        simulator = NIfTISimulator(file_path)
        if args.clear_state:
            simulator.clear_state()
       
        analysis_results = []
       
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
                "gif_path": gif_name
            }
            analysis_results.append(entry)
           
            if args.save_type != "None":
                output_path = os.path.join(args.output_dir, f"{base_name}_{sim_type}")
                if args.save_type == "3d":
                    output_path += ".nii.gz"
                simulator.save_data(data, args.save_type, args.axis, output_path)
                entry["output_path"] = output_path
           
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
                    "gif_path": gif_name
                }
                analysis_results.append(entry)
               
                if args.save_type != "None":
                    output_path = os.path.join(args.output_dir, f"{base_name}_{sim_type}")
                    if args.save_type == "3d":
                        output_path += ".nii.gz"
                    simulator.save_data(data, args.save_type, args.axis, output_path)
                    entry["output_path"] = output_path
               
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
                "gif_path": chained_gif_name
            }
            analysis_results.append(chained_entry)
           
            if args.save_type != "None":
                chained_output_path = os.path.join(args.output_dir, f"{base_name}_chained_{'_'.join(args.sim_type)}")
                if args.save_type == "3d":
                    chained_output_path += ".nii.gz"
                simulator.save_data(chained_data, args.save_type, args.axis, chained_output_path)
                chained_entry["output_path"] = chained_output_path
           
            print(f"Processed chained ({', '.join(args.sim_type)}): Shape {chained_data.shape}, GIF saved to {chained_gif_name}")

        with open(json_path, 'w') as f:
            json.dump(analysis_results, f, indent=4)
        print(f"Analysis results saved to {json_path}")

if __name__ == "__main__":
    cli = NIfTI_SingleFileCLI()
    cli.run()