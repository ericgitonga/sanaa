# 3d_art.py
import os
import sys
import subprocess
import pkg_resources


def check_and_install_dependencies():
    """Check for required dependencies and install/upgrade as needed."""
    # List of required packages with version constraints
    required_packages = ["numpy>=1.19.0", "matplotlib>=3.3.0", "imageio>=2.9.0", "Pillow>=8.0.0", "scipy>=1.5.0"]

    print("Checking and installing dependencies...")

    # Check existing packages
    installed = {pkg.key: pkg.version for pkg in pkg_resources.working_set}
    missing = []
    upgrade = []

    for package in required_packages:
        # Parse package name and version constraint
        if ">=" in package:
            name, version = package.split(">=")
            name = name.strip()
            min_version = version.strip()

            if name in installed:
                current_version = installed[name]
                # Compare versions to see if upgrade needed
                try:
                    if pkg_resources.parse_version(current_version) < pkg_resources.parse_version(min_version):
                        print(f"Package {name} needs upgrade: {current_version} -> {min_version}+")
                        upgrade.append(package)
                    else:
                        print(f"Package {name} is up to date ({current_version})")
                except Exception as e:
                    print(f"Error comparing versions for {name}: {e}")
                    upgrade.append(package)  # Add to upgrade list to be safe
            else:
                print(f"Package {name} not found, will install {package}")
                missing.append(package)
        else:
            name = package
            if name not in installed:
                print(f"Package {name} not found, will install")
                missing.append(package)
            else:
                print(f"Package {name} is installed ({installed[name]})")

    # Install missing packages
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            print("You may need to run this script with sudo or use a virtual environment.")
            sys.exit(1)

    # Upgrade packages
    if upgrade:
        print(f"Upgrading packages: {', '.join(upgrade)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + upgrade)
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading packages: {e}")
            print("You may need to run this script with sudo or use a virtual environment.")
            sys.exit(1)

    if not missing and not upgrade:
        print("All dependencies are already satisfied!")
    else:
        print("All dependencies are now installed and up to date!")

    # Check for FFmpeg
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
        print("FFmpeg is installed and available.")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("WARNING: FFmpeg is not installed or not in PATH. This is required for video output.")
        print("Please install FFmpeg from https://ffmpeg.org/download.html or use your system's package manager.")
        print("For example, on Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("On macOS with Homebrew: brew install ffmpeg")
        print("On Windows: Download from https://ffmpeg.org/download.html#build-windows")
        if input("Continue anyway? (y/n): ").lower() != "y":
            sys.exit(1)


# First, run the dependency check before importing any other modules
print("Checking dependencies before running...")
check_and_install_dependencies()

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
    This is a placeholder - modify based on your specific file types.
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
    """Recursively scan a directory and gather data from all files."""
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
    """Create a 3D visualization of the files and save as video."""
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
    for file_path in file_list:
        matrix = process_file_to_data(file_path)
        data_matrices.append(matrix)
        max_z_height = max(max_z_height, np.max(matrix))

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
    anim = animation.FuncAnimation(
        fig, update_plot, frames=len(data_matrices), fargs=(data_matrices, ax), interval=200, blit=False
    )

    # Save as video
    print(f"Saving animation to {output_video}...")
    writer = animation.FFMpegWriter(fps=15, bitrate=5000)
    anim.save(output_video, writer=writer)
    print(f"Video saved successfully to {output_video}")

    plt.close(fig)
    return output_video


def main():
    """Main entry point for the program."""
    import argparse

    parser = argparse.ArgumentParser(description="Create 3D visualization of files in a directory")
    parser.add_argument("directory", type=str, help="Directory to scan recursively")
    parser.add_argument("--output", type=str, default="file_visualization.mp4", help="Output video filename")
    parser.add_argument("--max-files", type=int, default=100, help="Maximum number of files to process")

    args = parser.parse_args()

    # Scan directory and get files
    file_list = scan_directory(args.directory)

    # Create visualization
    if file_list:
        video_path = create_3d_visualization(file_list, args.output, args.max_files)
        print(f"Visualization complete. Video saved to: {video_path}")
    else:
        print("No files found to visualize.")


if __name__ == "__main__":
    main()
