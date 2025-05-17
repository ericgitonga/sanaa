#!/usr/bin/env python3
"""
3D File Visualizer

This script recursively traverses a directory structure and converts files into
a flowing 3D visualization saved as a video. You can also add an MP3 audio file
to be synchronized with the animation.

First-time users must run setup.py before using this script to install all required dependencies.

Author: Eric Gitonga
Copyright: 2025 Eric Gitonga - May 16, 2025
License: MIT
Version: 0.1.0
"""

import os
import sys
import argparse
import subprocess
import tempfile

# Only import these modules after setup.py has been run to install them
try:
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib import animation
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401 - Needed for '3d' projection
    import imageio  # noqa: F401 - Required for matplotlib's FFMpegWriter
    from PIL import Image
    import scipy.ndimage as ndimage

    # Try importing MoviePy components - prioritize direct imports for Anaconda compatibility
    try:
        # For Anaconda environments, direct imports often work better than the .editor module
        # Try direct imports first (which we know are working from the setup script)
        try:
            from moviepy.video.io.VideoFileClip import VideoFileClip
            from moviepy.audio.io.AudioFileClip import AudioFileClip

            print("Using direct MoviePy component imports")
            moviepy_available = True
        except ImportError as core_err:
            # If direct imports fail, try the standard editor module
            try:
                from moviepy.editor import VideoFileClip, AudioFileClip

                print("Using moviepy.editor imports")
                moviepy_available = True
            except ImportError as editor_err:
                raise ImportError(f"Failed to import MoviePy components: {core_err} and {editor_err}")
    except ImportError as moviepy_err:
        print(f"Warning: MoviePy import failed: {moviepy_err}")
        print("Audio synchronization features will be disabled.")
        print("For Anaconda/Conda environments, try:")
        print("    conda install -c conda-forge moviepy ffmpeg decorator imageio-ffmpeg")
        print("For standard Python environments, try:")
        print("    pip install moviepy --upgrade --force-reinstall")
        moviepy_available = False

        class DummyClip:
            def __init__(self, *args, **kwargs):
                self.duration = 0

            def close(self):
                pass

            def subclip(self, *args):
                return self

            def set_audio(self, *args):
                return self

            def write_videofile(self, *args, **kwargs):
                print("Error: MoviePy not available - cannot create video with audio.")
                return None

        VideoFileClip = AudioFileClip = DummyClip
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Please run setup.py first to install all required dependencies:")
    print("    python setup.py")
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


def create_3d_visualization(
    file_list, output_video="file_visualization.mp4", max_files=100, audio_file=None, fps=15, duration=None
):
    """
    Create a 3D visualization of the files and save as video.

    Args:
        file_list (list): List of file paths to visualize
        output_video (str): Path for the output video file
        max_files (int): Maximum number of files to process
        audio_file (str, optional): Path to MP3 audio file to synchronize with the animation
        fps (int): Frames per second for the video output
        duration (float, optional): Duration to match video with audio (in seconds)

    Returns:
        str: Path to the created video file
    """
    # Limit the number of files to process to avoid excessive computation
    if len(file_list) > max_files:
        print(f"Limiting to {max_files} files out of {len(file_list)}")
        file_list = file_list[:max_files]

    # Determine duration if audio file is provided
    audio_duration = None
    if audio_file:
        try:
            print(f"Reading audio file: {audio_file}")
            audio_clip = AudioFileClip(audio_file)
            audio_duration = audio_clip.duration
            audio_clip.close()

            if duration is None:
                duration = audio_duration
                print(f"Setting animation duration to match audio: {duration:.2f} seconds")
            else:
                print(f"Using specified duration: {duration:.2f} seconds (audio is {audio_duration:.2f} seconds)")
        except Exception as e:
            print(f"Warning: Could not read audio file: {e}")
            audio_file = None

    # If duration is not set from audio, estimate it based on number of files
    if duration is None:
        # Default to about 10 seconds for small collections, up to 60 seconds for larger ones
        duration = min(10 + (len(file_list) / 10), 60)
        print(f"Setting animation duration to {duration:.2f} seconds")

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

    # Calculate the number of frames based on duration and fps
    num_frames = int(duration * fps)

    # Function to update the plot for each frame
    def update_plot(frame_num, data_matrices, plot):
        ax.clear()
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Data Value")
        ax.set_title(f"3D Visualization of Files - Frame {frame_num+1}/{num_frames}")

        # Calculate which file to display based on frame number and total duration
        # This ensures we spread the files evenly across the animation duration
        file_idx = min(int((frame_num / num_frames) * len(data_matrices)), len(data_matrices) - 1)

        # Take a slice of the data matrices to create a flowing effect
        # Show more files at once for a richer visualization
        window_size = min(6, len(data_matrices))
        start_idx = max(0, file_idx - (window_size - 1))
        end_idx = min(len(data_matrices), start_idx + window_size)

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
        ax.view_init(elev=30, azim=(frame_num * 2) % 360)

        return [surf]

    # Create animation
    print(f"Generating animation with {num_frames} frames at {fps} fps...")
    anim = animation.FuncAnimation(
        fig,
        update_plot,
        frames=num_frames,
        fargs=(data_matrices, ax),
        interval=1000 / fps,  # Interval in milliseconds
        blit=False,
    )

    # If audio is provided, we need to save to a temp file first, then combine with audio
    if audio_file and moviepy_available:
        temp_video = None
        final_output = output_video
        try:
            # Create temporary file for the silent video
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as temp:
                temp_video = temp.name

            # Save the animation without audio
            print("Saving animation to temporary file...")
            writer = animation.FFMpegWriter(fps=fps, bitrate=5000)
            anim.save(temp_video, writer=writer)

            # Close the matplotlib figure
            plt.close(fig)

            # Combine video with audio
            print(f"Adding audio from {audio_file}...")
            video_clip = VideoFileClip(temp_video)
            audio_clip = AudioFileClip(audio_file)

            # Adjust audio duration if needed
            if audio_clip.duration != video_clip.duration:
                if audio_clip.duration > video_clip.duration:
                    print(f"Trimming audio to match video duration ({video_clip.duration:.2f}s)")
                    audio_clip = audio_clip.subclip(0, video_clip.duration)
                else:
                    print(f"Audio shorter than video. Audio will end at {audio_clip.duration:.2f}s")

            # Set the audio for the video clip
            final_clip = video_clip.set_audio(audio_clip)

            # Write the final video with audio
            print(f"Saving final video with audio to {final_output}...")
            final_clip.write_videofile(final_output, codec="libx264", audio_codec="aac")

            # Close the clips
            video_clip.close()
            audio_clip.close()
            final_clip.close()

            # Remove the temporary file
            os.unlink(temp_video)

            print(f"Video with audio saved successfully to {final_output}")
            return final_output

        except Exception as e:
            print(f"Error adding audio to video: {e}")
            print("Falling back to saving video without audio...")
            if temp_video and os.path.exists(temp_video):
                try:
                    os.unlink(temp_video)
                except OSError as temp_err:
                    print(f"Warning: Could not remove temporary file {temp_video}: {temp_err}")

    # Save as video without audio (or if audio processing failed)
    print(f"Saving animation to {output_video}...")
    try:
        writer = animation.FFMpegWriter(fps=fps, bitrate=5000)
        anim.save(output_video, writer=writer)
        print(f"Video saved successfully to {output_video}")
    except Exception as e:
        print(f"Error saving video: {e}")
        print("Please ensure FFmpeg is properly installed and in your PATH.")
        return None

    plt.close(fig)
    return output_video


def validate_audio_file(audio_path):
    """
    Validate that the audio file exists and has a supported format.

    Args:
        audio_path (str): Path to the audio file

    Returns:
        bool: True if the file is valid, False otherwise
    """
    if not audio_path:
        return False

    if not os.path.isfile(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return False

    # Check file extension
    _, ext = os.path.splitext(audio_path)
    ext = ext.lower()

    if ext not in [".mp3", ".wav", ".ogg", ".aac", ".m4a"]:
        print(f"Error: Unsupported audio format: {ext}")
        print("Supported formats: .mp3, .wav, .ogg, .aac, .m4a")
        return False

    # Only try to read the file with moviepy if it's available
    if moviepy_available:
        try:
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            audio.close()
            print(f"Audio file validated: {os.path.basename(audio_path)} ({duration:.2f} seconds)")
            return True
        except Exception as e:
            print(f"Error: Could not read audio file: {e}")
            return False
    else:
        print("Audio file found but MoviePy is not available for processing.")
        print("Audio synchronization will be disabled.")
        return False


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
    parser.add_argument(
        "--audio", type=str, default=None, help="Path to MP3 audio file to synchronize with the animation"
    )
    parser.add_argument(
        "--duration",
        type=float,
        default=None,
        help="Duration of the animation in seconds (default: based on audio or files)",
    )
    parser.add_argument("--fps", type=int, default=15, help="Frames per second for the video output")

    args = parser.parse_args()

    # Validate directory
    if not os.path.isdir(args.directory):
        print(f"Error: {args.directory} is not a valid directory")
        return 1

    # Validate audio file if provided
    audio_file = None
    if args.audio:
        if validate_audio_file(args.audio):
            audio_file = args.audio
        else:
            print("Warning: Invalid audio file - proceeding without audio")

    # Scan directory and get files
    file_list = scan_directory(args.directory)

    # Create visualization
    if file_list:
        video_path = create_3d_visualization(
            file_list, args.output, args.max_files, audio_file=audio_file, fps=args.fps, duration=args.duration
        )

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
    print("3D File Visualizer")
    print("==================")
    print("Copyright © 2025 Eric Gitonga - May 16, 2025")
    print()

    # Check if FFmpeg is available
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        print("ERROR: FFmpeg is not installed or not in your PATH.")
        print("Please run setup.py first to check all dependencies:")
        print("    python setup.py")
        sys.exit(1)

    sys.exit(main())
