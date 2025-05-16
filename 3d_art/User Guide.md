# Usage Guide for 3D File Visualizer

Copyright © 2025 Eric Gitonga - May 16, 2025

# Project Structure

```
3d_file_visualizer/
├── 3d_art.py           # Main script for file visualization
├── dependencies.py     # Dependency management module
├── setup.py            # Installation and packaging script
├── README.md           # Project documentation
└── docs/
    └── technical_docs.md  # Technical documentation
```

# Installation Guide

## Requirements

- Python 3.6 or higher
- FFmpeg (for video encoding)

## Installation Methods

### Method 1: Direct Use

1. Clone the repository:
```bash
git clone https://github.com/yourusername/3d_file_visualizer.git
cd 3d_file_visualizer
```

2. Run the script:
```bash
python 3d_art.py /path/to/visualize
```

The script will automatically check for and install required Python dependencies.

### Method 2: Using pip

1. Clone the repository:
```bash
git clone https://github.com/yourusername/3d_file_visualizer.git
cd 3d_file_visualizer
```

2. Install using pip:
```bash
pip install -e .
```

3. Run the installed command:
```bash
3d-visualizer /path/to/visualize
```

### Method 3: Install FFmpeg

The script requires FFmpeg for video encoding. Install it based on your operating system:

#### Ubuntu/Debian:
```bash
sudo apt-get install ffmpeg
```

#### macOS (with Homebrew):
```bash
brew install ffmpeg
```

#### Windows:
Download from [FFmpeg's official site](https://ffmpeg.org/download.html#build-windows) and add it to your PATH.

## Verification

To verify the installation:

1. Run the dependency check:
```bash
python dependencies.py
```

2. Run a test visualization with a small directory:
```bash
python 3d_art.py /path/to/small/directory --max-files 10
```

You should see a file_visualization.mp4 file created in your current directory.

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

### "ModuleNotFoundError: No module named 'X'"
The automatic dependency installation failed. Try manually installing:
```bash
pip install numpy matplotlib imageio Pillow scipy
```

### "FFmpeg not found"
FFmpeg is not installed or not in your PATH. Install FFmpeg and ensure it's accessible from the command line.

### "Error saving video"
Check that FFmpeg is properly installed and in your PATH. Try running:
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
