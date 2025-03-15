#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import numpy as np 
import random

class Opts(object):
    def __init__(self):
        '''Paths'''
        self.i = '../Sample_Data/'          # MNI152_T1_2mm_brain.nii.gz input_path of input folder fo multiple files
        self.o = '../outputs/'         # output_path
        self.gif_dir = '../outputs/gifs/'
        #self.json_file = False
        self.verbose = True  # Controls print functions
        
        '''Axis'''
        # Axis Param  --fixed_range
        self.fixed_range = 'range'          # if range, Allows the simulator to randomly choose a value from with the upper and lower range
        
        '''Clear State'''
        # Clear State Param  --clear_state
        self.clear_state = True          # Clear simulator state before each file
        
        '''Axis'''
        # Axis Param  --axis
        self.axis = int(np.random.choice([0, 1, 2]))                      # Main axis for simulations
        
        '''Missing Slides'''
        # Missing Slides Param  --remove_param
        self.remove_param_upper = 15   #0.5      # maximum number or % of slides to remove
        self.remove_param_lower = 1    #0.01      # minimum number or % of slides to remove
        self.remove_param = self.get_type_value(
            self.remove_param_lower, 
            self.remove_param_upper
            )                # Number/fraction (e.g., 5 or 0.2) of slides to remove (missing_slides) fraction must be less than 1
        
        
        
        '''Wrong Sequence'''
        # Wrong Sequence Param  --shuffle_param
        self.shuffle_param_upper = 0.5          # maximum number or % of slides to shuffle
        self.shuffle_param_lower = 0.01         # minimum number or % of slides to shuffle
        self.shuffle_param = self.get_type_value(
            self.shuffle_param_lower, 
            self.shuffle_param_upper
            )                  # Number/fraction  (e.g., 5 or 0.2) of slides to shuffle (wrong_sequence), fraction must be less than 1
        
        
        '''Mixed Axis'''
        # Weight Param Param  --weight_param
        self.weight_param_upper = 0.3           # maximum number or % of slides to draw from a different axis
        self.weight_param_lower = 0.01          # minimum number or % of slides to draw from a different axis
        self.weight_param = self.get_type_value(
            self.weight_param_lower, 
            self.weight_param_upper
            )               # Number/fraction  (e.g., 5 or 0.2) of slides to shuffle (wrong_sequence), fraction must be less than 1
        
        # Mixed Axis List Param  --mixed_axis_list
        self.axis_string_list = ['0,1', '0,2', '1,0', '2,0', '1,2', '2,1', '0,1,2', '0,2,1', '1,0,2', '1,2,0', '2,0,1', '2,1,0']                # Must be interger Axes for mixed_axis (e.g., 0 1 2) e.g '0,1' or '0,2' or '1,2' or '0,1,2'
        self.mixed_axis_list = self.select_mixed_axis()
        
        '''Save Image'''
        # Save Type Param  --save_type
        self.save_type = 'None'                   # choices=["3d", "jpeg", "None"] 3d saves as nifti, jpeg saves slides as jpeg
        
        '''Number of simulation image'''
        # sim_img Param  --sim_img
        self.sim_img = 'multi_img'             # Number simulation image (single_img: 1, multi_img: 2+) choices=["single_img", "multi_img"]
        
        '''Simulation Mode'''
        # sim_mode Param  --sim_mode
        self.sim_mode = 'chained'                # Simulation mode (single: 1, independent/chained: 2+) choices=["single", "independent", "chained"]
        
        '''Simulation types'''
        # sim_type Param  --sim_type
        # Take a list for independent and chain simulation and string for single
        self.sim_type = ["missing_slides", "wrong_sequence", "mixed_axis"] #'wrong_sequence'        # or ["missing_slides", "wrong_sequence", "mixed_axis"] for independent or chained       # Simulation types choices=["missing_slides", "wrong_sequence", "mixed_axis"]

    def get_type_value(self, lower, upper):
        """Generates a random weight parameter, ensuring it's an int if possible."""
        value = np.random.uniform(lower, upper)
        return self.int_or_float(value)
    
    def int_or_float(self, value):
        """Converts a value to int if possible, otherwise returns float."""
        if 0 <= value <= 1:
            k = float(value)
        else:
            k = int(value)
        return k

    
    def select_mixed_axis(self):
        """
        Selects a mixed axis string from a list based on the given axis.

        Args:
            axis: The starting axis (0, 1, or 2).
            axis_string_list: A list of axis strings (e.g., ['0,1', '0,2', '1,0', '2,0', ...]).

        Returns:
            A list of integers representing the selected mixed axis, or None if no match is found.
        """
        matching_strings = []
        for axis_string in self.axis_string_list:
            if axis_string.startswith(str(self.axis)):
                matching_strings.append(axis_string)

        if not matching_strings:
            return None  # No matching axis string found

        selected_string = random.choice(matching_strings) #choose a random matching string.

        if ',' in selected_string:
            # Comma-separated values
            mixed_axis_list = [int(x) for x in selected_string.split(',')]
        else:
            # Individual digits
            mixed_axis_list = [int(x) for x in selected_string]

        return mixed_axis_list




