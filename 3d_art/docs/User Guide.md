# Usage Guide for 3D File Visualizer

Copyright © 2025 Eric Gitonga - May 16, 2025

This guide provides comprehensive instructions for using the 3D File Visualizer tool, including the new audio synchronization feature.

## Project Structure

```
3d_file_visualizer/
├── 3d_art.py           # Main script for file visualization
├── setup.py            # Setup and dependency installation script
├── README.md           # Project documentation
└── docs/
    └── technical_docs.md  # Technical documentation
    └── usage_guide.md     # This file
```

## Installation Guide

### Requirements

- Python 3.6 or higher
- FFmpeg (for video encoding)

### First-Time Installation

Before using the 3D File Visualizer, you **must run the setup script** to install all required dependencies:

```bash
python setup.py
```

This will:
1. Check for and install all required Python packages (numpy, matplotlib, imageio, Pillow, scipy, moviepy)
2. Verify that FFmpeg is installed and available
3. Provide instructions if any dependencies are missing

If the setup fails due to missing FFmpeg, install it based on your operating system:

- **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
- **macOS (with Homebrew)**: `brew install ffmpeg`
- **Windows**: Download from [FFmpeg's official site](https://ffmpeg.org/download.html#build-windows) and add it to your PATH

### Verification

To verify that everything is installed correctly, run:

```bash
python 3d_art.py --help
```

You should see the help message with available command-line options.

## Basic Usage

```bash
python 3d_art.py /path/to/directory
```

This will scan the specified directory recursively and create a `file_visualization.mp4` video.

## Advanced Options

### Specifying Output File

```bash
python 3d_art.py /path/to/directory --output my_visualization.mp4
```

### Limiting the Number of Files

For large directories, limit the number of files to process:

```bash
python 3d_art.py /path/to/directory --max-files 50
```

### Adding an Audio Track

You can synchronize an MP3 audio file with your visualization:

```bash
python 3d_art.py /path/to/directory --audio music.mp3
```

The video duration will automatically match the audio duration.

### Specifying Video Duration

Set a custom duration for the animation (in seconds):

```bash
python 3d_art.py /path/to/directory --duration 45.5
```

If you specify both an audio file and duration, the audio will be trimmed or the video will end before the audio does, depending on which is longer.

### Adjusting Video Frame Rate

Change the frames per second for smoother animation:

```bash
python 3d_art.py /path/to/directory --fps 30
```

### Combining Multiple Options

All options can be combined:

```bash
python 3d_art.py /path/to/directory --output epic_viz.mp4 --max-files 200 --audio soundtrack.mp3 --duration 60 --fps 24
```

## Visualizing Different Types of Content

### Source Code Repositories
```bash
python 3d_art.py /path/to/code/repo --output code_visualization.mp4
```

Try adding upbeat electronic music for a futuristic coding visualization:
```bash
python 3d_art.py /path/to/code/repo --audio electronic.mp3
```

### Image Collections
```bash
python 3d_art.py /path/to/photos --output photo_visualization.mp4 --fps 24
```

Family photos look great with a nostalgic soundtrack:
```bash
python 3d_art.py /path/to/family_photos --audio nostalgic_piano.mp3
```

### Mixed Content
```bash
python 3d_art.py /path/to/documents --output docs_visualization.mp4
```

### Creating a Perfect Music Video
For a precisely timed music video visualization:
```bash
python 3d_art.py /path/to/media --audio your_favorite_song.mp3 --fps 30 --max-files 300
```

## Advanced Configuration

To modify the visualization parameters, edit the following in `3d_art.py`:

### Changing the Surface Plot Properties
```python
# Find this section in create_3d_visualization():
surf = ax.plot_surface(
    x, y, z,
    rstride=1, cstride=1,  # Adjust these for performance
    alpha=alpha,
    cmap='viridis',  # Change colormap here (try 'plasma', 'magma', or 'inferno')
    linewidth=0, antialiased=True
)
```

### Modifying Animation Parameters
```python
# Find this section in create_3d_visualization():
anim = animation.FuncAnimation(
    fig, update_plot,
    frames=num_frames,
    fargs=(data_matrices, ax),
    interval=1000/fps,  # Interval in milliseconds
    blit=False
)

# For video quality:
writer = animation.FFMpegWriter(fps=fps, bitrate=5000)  # Increase bitrate for higher quality
```

### Changing the Camera Angle
```python
# Find this line in update_plot():
ax.view_init(elev=30, azim=(frame_num * 2) % 360)  # Adjust elevation and rotation speed
```

### Audio Synchronization Parameters

If you want to modify how the files are synchronized with the audio:

```python
# Find the sliding window size in update_plot:
window_size = min(6, len(data_matrices))  # Increase to show more files at once

# Change file progression timing:
file_idx = min(int((frame_num / num_frames) * len(data_matrices)), len(data_matrices) - 1)
```

## Supported Audio Formats

The tool supports the following audio formats:
- MP3 (.mp3)
- WAV (.wav)
- OGG (.ogg)
- AAC (.aac)
- M4A (.m4a)

## Troubleshooting

### Common Issues and Solutions

#### "Please run setup.py first"
You haven't run the setup script. Run `python setup.py` to install all dependencies.

#### "Error importing modules"
The required Python packages weren't properly installed. Try running `python setup.py` again, or install them manually:
```bash
pip install numpy matplotlib imageio Pillow scipy moviepy
```

#### "MoviePy import failed"
This is a known issue, especially in Anaconda/Conda environments. Try one of these solutions:

**For Anaconda/Conda environments:**
```bash
conda install -c conda-forge moviepy ffmpeg decorator imageio-ffmpeg
```

**For standard Python environments:**
```bash
pip install moviepy --upgrade --force-reinstall
pip install decorator>=4.0.2 imageio-ffmpeg>=0.4.4
```

Note: Even if MoviePy cannot be installed properly, the tool will still work without audio features.

#### "FFmpeg is not installed or not in your PATH"
FFmpeg is missing or not accessible. Install FFmpeg and ensure it's in your system PATH.

#### "Error saving video"
Check that FFmpeg is properly installed and accessible by running:
```bash
ffmpeg -version
```

#### "Error adding audio to video"
This can happen when there's an issue with the audio file or with MoviePy. Try a different audio file or check if MoviePy is installed correctly:
```bash
pip install --upgrade moviepy
```

#### "Invalid audio file"
The provided audio file couldn't be read. Make sure it's a valid MP3, WAV, OGG, AAC, or M4A file. Try converting it to a different format.

#### "Permission denied"
You might not have read access to some files in the directory. Try running with appropriate permissions or use a different directory.

## Performance Tips

- Start with a small `--max-files` value and increase gradually
- For large directories, visualize specific subdirectories instead
- Close memory-intensive applications before running large visualizations
- For slow machines, create a lower resolution video by modifying the figure size in the code
- When using audio, longer visualizations with higher FPS require more processing power and memory
