import numpy as np
import imageio
from pathlib import Path

def save_gif(data, output_name, axis=0, duration=0.1, percentage=0.3):
    """
    Save a GIF from the first percentage of slides along specified axis.
    
    Args:
        data (np.ndarray): 3D numpy array of NIfTI data
        output_name (str): Name for the output GIF file
        axis (int): Axis along which to take slices (0, 1, or 2)
        duration (float): Seconds per frame in GIF
        percentage (float): Fraction of slices to include (0-1)
    """
    #Path('gifs').mkdir(exist_ok=True)
    
    n_slices = data.shape[axis]
    n_frames = int(n_slices * percentage)
    
    frames = []
    if axis == 0:
        slices = data[:n_frames, :, :]
    elif axis == 1:
        slices = data[:, :n_frames, :]
    else:
        slices = data[:, :, :n_frames]
    
    for i in range(n_frames):
        frame = slices[i, :, :] if axis == 0 else \
                slices[:, i, :] if axis == 1 else \
                slices[:, :, i]
        frame = (frame - frame.min()) / (frame.max() - frame.min() + 1e-10) * 255
        frame = frame.astype(np.uint8)
        rot_frame = np.rot90(frame, k=1)
        frames.append(rot_frame)
    
    gif_path = f'../gifs/{output_name}.gif'
    imageio.mimsave(gif_path, frames, duration=duration)
    print(f"Saved GIF: {gif_path}")