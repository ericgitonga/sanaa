# Usage Guide for 3D File Visualizer

Copyright © 2025 Eric Gitonga - May 16, 2025

# Project Structure

```
3d_file_visualizer/
├── 3d_art.py           # Main script for file visualization
├── setup.py            # Setup and dependency installation script
├── README.md           # Project documentation
└── docs/
    └── technical_docs.md  # Technical documentation
    └── usage_guide.md     # This file
```

# Installation Guide

## Requirements

- Python 3.6 or higher
- FFmpeg (for video encoding)

## First-Time Installation

Before using the 3D File Visualizer, you **must run the setup script** to install all required dependencies:

```bash
python setup.py
```

This will:
1. Check for and install all required Python packages (numpy, matplotlib, imageio, Pillow, scipy)
2. Verify that FFmpeg is installed and available
3. Provide instructions if any dependencies are missing

If the setup fails due to missing FFmpeg, install it based on your operating system:

- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **macOS (with Homebrew)**: `brew install ffmpeg`
- **Windows**: Download from [FFmpeg's official site](https://ffmpeg.org/download.html#build-windows) and add it to your PATH

## Verification

To verify that everything is installed correctly, run:

```bash
python 3d_art.py --help
```

You should see the help message with available command-line options.

# Usage Examples

## Basic Usage

```bash
python 3d_art.py /path/to/directory
```

This will scan the specified directory recursively and create a `file_visualization.mp4` video.

## Specifying Output File

```bash
python 3d_art.py /path/to/directory --output my_visualization.mp4
```

## Limiting the Number of Files

For large directories, limit the number of files to process:

```bash
python 3d_art.py /path/to/directory --max-files 50
```

## Visualizing Different Types of Directories

### Source Code Repositories
```bash
python 3d_art.py /path/to/code/repo --output code_visualization.mp4
```

### Image Collections
```bash
python 3d_art.py /path/to/photos --output photo_visualization.mp4
```

### Mixed Content
```bash
python 3d_art.py /path/to/documents --output docs_visualization.mp4
```

# Troubleshooting

## Common Issues and Solutions

### "Please run setup.py first"
You haven't run the setup script. Run `python setup.py` to install all dependencies.

### "Error importing modules"
The required Python packages weren't properly installed. Try running `python setup.py` again, or install them manually:
```bash
pip install numpy matplotlib imageio Pillow scipy
```

### "FFmpeg is not installed or not in your PATH"
FFmpeg is missing or not accessible. Install FFmpeg and ensure it's in your system PATH.

### "Error saving video"
Check that FFmpeg is properly installed and accessible by running:
```bash
ffmpeg -version
```

### "Permission denied"
You might not have read access to some files in the directory. Try running with appropriate permissions or use a different directory.

## Performance Tips

- Start with a small `--max-files` value and increase gradually
- For large directories, visualize specific subdirectories instead
- Close memory-intensive applications before running large visualizations
- For slow machines, create a lower resolution video by modifying the figure size in the code

# Advanced Configuration

To modify the visualization parameters, edit the following in `3d_art.py`:

## Changing the Surface Plot Properties
```python
# Find this section in create_3d_visualization():
surf = ax.plot_surface(
    x, y, z,
    rstride=1, cstride=1,  # Adjust these for performance
    alpha=alpha,
    cmap='viridis',  # Change colormap here
    linewidth=0, antialiased=True
)
```

## Modifying Animation Parameters
```python
# Find this section in create_3d_visualization():
anim = animation.FuncAnimation(
    fig, update_plot,
    frames=len(data_matrices),
    fargs=(data_matrices, ax),
    interval=200,  # Frame duration in ms
    blit=False
)

# For video quality:
writer = animation.FFMpegWriter(fps=15, bitrate=5000)  # Adjust fps and bitrate
```

## Changing the Camera Angle
```python
# Find this line in update_plot():
ax.view_init(elev=30, azim=frame_num % 360)  # Adjust elevation and azimuth
```
