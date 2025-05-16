#!/usr/bin/env python3
"""
3D File Visualizer

This script recursively traverses a directory structure and converts files into
a flowing 3D visualization saved as a video.

Author: Eric Gitonga
Copyright: 2025 Eric Gitonga - May 16, 2025
License: MIT
Version: 0.1.0
"""

import os
import sys
import argparse

# First, make sure dependencies are available
print("Checking dependencies before running...")
try:
    from dependencies import check_and_install_dependencies

    check_and_install_dependencies()
except ImportError:
    # If dependencies.py is not in the path, try to import it directly
    try:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "dependencies", os.path.join(os.path.dirname(__file__), "dependencies.py")
        )
        dependencies = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(dependencies)
        dependencies.check_and_install_dependencies()
    except Exception as e:
        print(f"Error importing dependencies module: {e}")
        print("Please ensure dependencies.py is available in the same directory.")
        sys.exit(1)

# Only import these modules after ensuring they're installed
try:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 - Needed for '3d' projection
    import imageio  # noqa: F401 - Required for matplotlib's FFMpegWriter
    from PIL import Image
    import scipy.ndimage as ndimage
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Something went wrong with the dependency installation. Please try installing manually:")
    print("pip install numpy matplotlib imageio Pillow scipy")
    sys.exit(1)


def process_file_to_data(file_path):
    """
    Convert a file to numerical data that can be visualized.

    This function processes different file types:
    - Images are converted to grayscale arrays
    - Text/CSV files are parsed as numerical data when possible
    - Other files generate data based on file metadata

    Args:
        file_path (str): Path to the file to process

    Returns:
        numpy.ndarray: A 2D numerical array representing the file
    """
    ext = os.path.splitext(file_path)[1].lower()

    if ext in [".jpg", ".jpeg", ".png", ".bmp", ".tif", ".tiff"]:
        # For image files, convert to grayscale data
        try:
            img = np.array(Image.open(file_path).convert("L"))
            # Resize to manageable dimensions if needed
            if img.shape[0] > 100 or img.shape[1] > 100:
                img = ndimage.zoom(img, 100 / max(img.shape[0], img.shape[1]))
            return img
        except Exception as e:
            print(f"Could not process image {file_path}: {e}")
            return np.zeros((10, 10))

    elif ext in [".txt", ".csv", ".dat"]:
        # For text files, try to parse as numerical data
        try:
            return np.loadtxt(file_path)
        except (ValueError, OSError, IOError) as e:
            # Fixed: Use specific exceptions instead of bare except
            print(f"Could not parse file {file_path} as numerical data: {e}")
            # If it fails, convert file size and modification time to a small matrix
            stats = os.stat(file_path)
            size = stats.st_size
            mtime = stats.st_mtime
            return np.array([[size % 100, mtime % 100], [mtime % 50, size % 50]])
    else:
        # For other files, use file metadata to create synthetic data
        stats = os.stat(file_path)
        size = stats.st_size
        mtime = stats.st_mtime
        # Create a small matrix based on file attributes
        rows = min(max(int(size / 1000), 5), 50)
        cols = min(max(int(mtime % 100), 5), 50)
        return np.fromfunction(lambda i, j: (i * j + size + mtime) % 255, (rows, cols))


def scan_directory(directory):
    """
    Recursively scan a directory and gather data from all files.

    Args:
        directory (str): Path to the directory to scan

    Returns:
        list: List of full paths to all files found
    """
    all_files = []
    total_size = 0

    for root, dirs, files in os.walk(directory):
        for file in files:
            full_path = os.path.join(root, file)
            all_files.append(full_path)
            total_size += os.path.getsize(full_path)

    print(f"Found {len(all_files)} files with total size {total_size / (1024*1024):.2f} MB")
    return all_files


def create_3d_visualization(file_list, output_video="file_visualization.mp4", max_files=100):
    """
    Create a 3D visualization of the files and save as video.

    Args:
        file_list (list): List of file paths to visualize
        output_video (str): Path for the output video file
        max_files (int): Maximum number of files to process

    Returns:
        str: Path to the created video file
    """
    # Limit the number of files to process to avoid excessive computation
    if len(file_list) > max_files:
        print(f"Limiting to {max_files} files out of {len(file_list)}")
        file_list = file_list[:max_files]

    # Create figure and 3D axis
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Process the files and collect data
    data_matrices = []
    max_z_height = 0

    print("Processing files...")
    for i, file_path in enumerate(file_list):
        print(f"Processing file {i+1}/{len(file_list)}: {os.path.basename(file_path)}", end="\r")
        matrix = process_file_to_data(file_path)
        data_matrices.append(matrix)
        max_z_height = max(max_z_height, np.max(matrix))
    print("\nFile processing complete.")

    # Set up the plot
    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Data Value")
    ax.set_title("3D Visualization of Files")

    # Set consistent limits for the plot
    max_x = max([matrix.shape[0] for matrix in data_matrices])
    max_y = max([matrix.shape[1] for matrix in data_matrices])
    ax.set_xlim(0, max_x)
    ax.set_ylim(0, max_y)
    ax.set_zlim(0, max_z_height)

    # Function to update the plot for each frame
    def update_plot(frame_num, data_matrices, plot):
        ax.clear()
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Data Value")
        ax.set_title(f"3D Visualization of Files - Frame {frame_num+1}/{len(data_matrices)}")

        # Take a slice of the data matrices to create a flowing effect
        start_idx = max(0, frame_num - 5)
        end_idx = min(len(data_matrices), frame_num + 1)

        # Plot each matrix with an offset in the z-direction
        for i, idx in enumerate(range(start_idx, end_idx)):
            matrix = data_matrices[idx]
            x = np.arange(matrix.shape[0])
            y = np.arange(matrix.shape[1])
            x, y = np.meshgrid(x, y)
            z = matrix.T

            # Add a fade effect for older matrices
            alpha = 0.2 + 0.8 * (i / (end_idx - start_idx))

            # Plot the surface with a color based on the file index
            surf = ax.plot_surface(
                x, y, z, rstride=1, cstride=1, alpha=alpha, cmap="viridis", linewidth=0, antialiased=True
            )

        ax.set_xlim(0, max_x)
        ax.set_ylim(0, max_y)
        ax.set_zlim(0, max_z_height)

        # Rotate view angle for dynamic effect
        ax.view_init(elev=30, azim=frame_num % 360)

        return [surf]

    # Create animation
    print("Generating animation...")
    anim = animation.FuncAnimation(
        fig, update_plot, frames=len(data_matrices), fargs=(data_matrices, ax), interval=200, blit=False
    )

    # Save as video
    print(f"Saving animation to {output_video}...")
    try:
        writer = animation.FFMpegWriter(fps=15, bitrate=5000)
        anim.save(output_video, writer=writer)
        print(f"Video saved successfully to {output_video}")
    except Exception as e:
        print(f"Error saving video: {e}")
        print("Please ensure FFmpeg is properly installed and in your PATH.")
        return None

    plt.close(fig)
    return output_video


def main():
    """
    Main entry point for the program.

    Parses command line arguments and runs the visualization process.
    """
    parser = argparse.ArgumentParser(
        description="Create 3D visualization of files in a directory",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("directory", type=str, help="Directory to scan recursively")
    parser.add_argument("--output", type=str, default="file_visualization.mp4", help="Output video filename")
    parser.add_argument("--max-files", type=int, default=100, help="Maximum number of files to process")

    args = parser.parse_args()

    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        return 1

    # Scan directory and get files
    file_list = scan_directory(args.directory)

    # Create visualization
    if file_list:
        video_path = create_3d_visualization(file_list, args.output, args.max_files)
        if video_path:
            print(f"Visualization complete. Video saved to: {video_path}")
            return 0
        else:
            print("Visualization failed.")
            return 1
    else:
        print("No files found to visualize.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
