# 3D File Visualizer

A simple Python tool that recursively scans directories and creates 3D visualizations of files as a flowing video animation.

Copyright © 2025 Eric Gitonga - May 16, 2025

## What is this?

This tool takes a directory as input, scans it recursively for all files, and creates a 3D visualization where each file becomes a surface plot in a flowing animation. The result is saved as an MP4 video.

## Installation

For first-time users, you **must run the setup script first** to install all required dependencies:

```bash
# Install required dependencies
python setup.py
```

This will check for and install all required Python packages and verify that FFmpeg is installed.

## Usage

After running setup.py, you can use the main script:

```bash
# Run the script on a directory
python 3d_art.py /path/to/your/directory

# Specify output file
python 3d_art.py /path/to/your/directory --output custom_name.mp4

# Limit number of files processed
python 3d_art.py /path/to/your/directory --max-files 50

# Add an audio track to the visualization
python 3d_art.py /path/to/your/directory --audio your_music.mp3

# Specify a custom duration for the video
python 3d_art.py /path/to/your/directory --duration 30.0

# Set custom frames per second
python 3d_art.py /path/to/your/directory --fps 30
```

## Troubleshooting

- **Setup failed**: If setup.py reports missing dependencies, try installing them manually: `pip install numpy matplotlib imageio Pillow scipy`

- **FFmpeg not found**: Install FFmpeg from https://ffmpeg.org/download.html or via your system's package manager.

- **Memory errors**: Use the `--max-files` option to limit the number of files processed.

## Documentation

For more detailed information, see:

- `technical_docs.md` - Full technical documentation
- `usage_guide.md` - Detailed usage examples and configurations

## License

This project is licensed under the MIT License. Copyright © 2025 Eric Gitonga - May 16, 2025
