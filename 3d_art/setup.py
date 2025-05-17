#!/usr/bin/env python3
"""
3D File Visualizer - Setup Script

This script installs all required dependencies for the 3D File Visualizer.
It checks for the presence of required packages and installs or upgrades them as needed.

First-time users must run this script before running 3d_art.py.

Usage:
    python setup.py

Dependencies:
    - numpy (>=1.19.0)
    - matplotlib (>=3.3.0)
    - imageio (>=2.9.0)
    - Pillow (>=8.0.0)
    - scipy (>=1.5.0)
    - moviepy (>=1.0.3)
    - FFmpeg (external dependency, must be installed separately)

Author: Eric Gitonga
Copyright: 2025 Eric Gitonga - May 16, 2025
License: MIT
"""

from setuptools import setup, find_packages
import subprocess
import sys
import pkg_resources
import importlib
import os
import importlib.util


def is_module_available(module_name):
    """Check if a module is available without importing it."""
    return importlib.util.find_spec(module_name) is not None


def check_and_install_dependencies():
    """
    Check for required dependencies and install/upgrade as needed.

    This function:
    1. Lists all required packages with minimum version requirements
    2. Checks which packages are already installed and their versions
    3. Determines which packages need to be installed or upgraded
    4. Uses pip to install missing packages and upgrade outdated ones
    5. Checks for FFmpeg installation (required for video output)

    Returns:
        bool: True if all dependencies are satisfied, False otherwise
    """
    # List of required packages with version constraints
    required_packages = [
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "imageio>=2.9.0",
        "Pillow>=8.0.0",
        "scipy>=1.5.0",
        "moviepy>=1.0.3",  # Added for audio synchronization
    ]

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
    install_success = True
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        try:
            # Force reinstall option for moviepy to ensure all its components are properly installed
            reinstall_opts = []
            if "moviepy" in " ".join(missing):
                print("Ensuring proper moviepy installation with --force-reinstall")
                reinstall_opts = ["--force-reinstall"]

            # Install with pip
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + reinstall_opts + missing)

            # Install extra dependencies for moviepy that might be needed
            if "moviepy" in " ".join(missing):
                try:
                    # Check if moviepy.editor module is available
                    if is_module_available("moviepy.editor"):
                        print("Verified moviepy.editor module is available")
                    else:
                        print("Warning: moviepy installed but moviepy.editor module not found")
                        print("Trying to check core component availability...")

                        # Check if core components are available
                        video_clip_available = is_module_available("moviepy.video.io.VideoFileClip")
                        audio_clip_available = is_module_available("moviepy.audio.io.AudioFileClip")

                        if video_clip_available and audio_clip_available:
                            print("Successfully verified MoviePy core components are available!")
                        else:
                            print("Warning: Some MoviePy core components might be missing")

                            # Check if we're in a conda environment
                            in_conda = os.environ.get("CONDA_PREFIX") is not None
                            if in_conda:
                                print("Detected Anaconda/Conda environment.")
                                print("Installing additional dependencies with conda...")
                                try:
                                    subprocess.check_call(
                                        [
                                            "conda",
                                            "install",
                                            "-y",
                                            "-c",
                                            "conda-forge",
                                            "moviepy",
                                            "ffmpeg",
                                            "decorator",
                                            "imageio-ffmpeg",
                                        ]
                                    )
                                except subprocess.CalledProcessError as e3:
                                    print(f"Error installing with conda: {e3}")
                            else:
                                print("Installing additional dependencies...")
                                try:
                                    # Install decorator package which moviepy depends on
                                    subprocess.check_call(
                                        [sys.executable, "-m", "pip", "install", "decorator>=4.0.2", "--upgrade"]
                                    )
                                    # Install imageio-ffmpeg which moviepy might need
                                    subprocess.check_call(
                                        [sys.executable, "-m", "pip", "install", "imageio-ffmpeg>=0.4.4", "--upgrade"]
                                    )
                                    # Reinstall moviepy
                                    subprocess.check_call(
                                        [sys.executable, "-m", "pip", "install", "moviepy", "--force-reinstall"]
                                    )
                                except subprocess.CalledProcessError as e4:
                                    print(f"Error installing moviepy dependencies: {e4}")
                                    install_success = False
                except ImportError as e:
                    print(f"Warning: moviepy import check failed: {e}")
                    print("Installing additional dependencies...")
                    # Similar to above, install additional deps
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            print("You may need to run this script with sudo or use a virtual environment.")
            install_success = False

    # Upgrade packages
    if upgrade:
        print(f"Upgrading packages: {', '.join(upgrade)}")
        try:
            # Force reinstall for moviepy to ensure all components are installed
            reinstall_opts = []
            if "moviepy" in " ".join(upgrade):
                print("Ensuring proper moviepy installation with --force-reinstall")
                reinstall_opts = ["--force-reinstall"]

            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + reinstall_opts + upgrade)

            # Verify moviepy installation if it was upgraded
            if "moviepy" in " ".join(upgrade):
                # Check if moviepy.editor module is available
                if is_module_available("moviepy.editor"):
                    print("Verified moviepy.editor module is available")
                else:
                    print("Warning: moviepy installed but moviepy.editor module not found")
                    print("Trying to check core component availability...")

                    # Check if core components are available
                    video_clip_available = is_module_available("moviepy.video.io.VideoFileClip")
                    audio_clip_available = is_module_available("moviepy.audio.io.AudioFileClip")

                    if video_clip_available and audio_clip_available:
                        print("Successfully verified MoviePy core components are available!")
                    else:
                        print("Warning: Some MoviePy core components might be missing")

                        # Check if we're in a conda environment
                        in_conda = os.environ.get("CONDA_PREFIX") is not None
                        if in_conda:
                            print("Detected Anaconda/Conda environment.")
                            print("Installing additional dependencies with conda...")
                            try:
                                subprocess.check_call(
                                    [
                                        "conda",
                                        "install",
                                        "-y",
                                        "-c",
                                        "conda-forge",
                                        "moviepy",
                                        "ffmpeg",
                                        "decorator",
                                        "imageio-ffmpeg",
                                    ]
                                )
                            except subprocess.CalledProcessError as e3:
                                print(f"Error installing with conda: {e3}")
                        else:
                            print("Installing additional dependencies...")
                            try:
                                # Install decorator package which moviepy depends on
                                subprocess.check_call(
                                    [sys.executable, "-m", "pip", "install", "decorator>=4.0.2", "--upgrade"]
                                )
                                # Install imageio-ffmpeg which moviepy might need
                                subprocess.check_call(
                                    [sys.executable, "-m", "pip", "install", "imageio-ffmpeg>=0.4.4", "--upgrade"]
                                )
                                # Reinstall moviepy
                                subprocess.check_call(
                                    [sys.executable, "-m", "pip", "install", "moviepy", "--force-reinstall"]
                                )
                            except subprocess.CalledProcessError as e4:
                                print(f"Error installing moviepy dependencies: {e4}")
                                install_success = False
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading packages: {e}")
            print("You may need to run this script with sudo or use a virtual environment.")
            install_success = False

    if not missing and not upgrade:
        print("All Python dependencies are already satisfied!")
    elif install_success:
        print("All Python dependencies are now installed and up to date!")

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

        # Try to find ffmpeg in common locations
        common_paths = [
            "/usr/bin/ffmpeg",
            "/usr/local/bin/ffmpeg",
            "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
            os.path.expanduser("~/ffmpeg/bin/ffmpeg"),
        ]

        for path in common_paths:
            if os.path.exists(path):
                print(f"Found FFmpeg at {path}, but it's not in your PATH.")
                print(f"Add this directory to your PATH: {os.path.dirname(path)}")
                break

        install_success = False

    return install_success


# Run the dependency check and installation when this script is executed directly
if __name__ == "__main__":
    print("3D File Visualizer - Setup")
    print("==========================")
    print("This script will install all required dependencies for the 3D File Visualizer.")
    print("Copyright © 2025 Eric Gitonga - May 16, 2025")
    print()

    success = check_and_install_dependencies()
    if success:
        # Verify critical imports work properly after installation
        all_imports_ok = True
        try:
            # Check if moviepy.editor module is available
            editor_available = is_module_available("moviepy.editor")
            if editor_available:
                print("\nVerified moviepy.editor module is available!")
            else:
                print("\nWarning: moviepy.editor could not be imported")
                print("Trying to check core component availability...")

                # Check if core components are available
                video_clip_available = is_module_available("moviepy.video.io.VideoFileClip")
                audio_clip_available = is_module_available("moviepy.audio.io.AudioFileClip")

                if video_clip_available and audio_clip_available:
                    print("Successfully verified MoviePy core components are available!")
                    print("The 3D File Visualizer will use these imports instead.")
                    all_imports_ok = True
                else:
                    all_imports_ok = False
                    print("Error verifying MoviePy core components availability")

                    # Check if we're in a conda environment and provide specific advice
                    in_conda = os.environ.get("CONDA_PREFIX") is not None
                    if in_conda:
                        print("\nDetected Anaconda/Conda environment!")
                        print("For Conda environments, try installing moviepy from conda-forge:")
                        print("    conda install -c conda-forge moviepy ffmpeg decorator imageio-ffmpeg")
                    else:
                        print("\nTry manually installing the following packages:")
                        print("    pip install decorator>=4.0.2 imageio-ffmpeg>=0.4.4")
                        print("    pip install moviepy --upgrade --force-reinstall")
        except Exception as e:
            all_imports_ok = False
            print(f"\nUnexpected error when checking MoviePy installation: {e}")
            print("The 3D File Visualizer will still work, but audio features will be disabled.")

        if all_imports_ok:
            print("\nSetup complete! All dependencies are installed.")
            print("You can now run the 3D File Visualizer with: python 3d_art.py /path/to/directory")
        else:
            print("\nSetup partially complete. Audio features may not be available.")
            print("You can still run the visualizer, but audio synchronization will be disabled.")
            print("Run the program with: python 3d_art.py /path/to/directory")
    else:
        print("\nSetup incomplete. Please install missing dependencies manually.")
        print("You may still be able to run the visualizer with limited functionality.")
        sys.exit(1)

# Setup configuration for packaging
setup(
    name="3d_file_visualizer",
    version="0.1.0",
    author="Eric Gitonga",
    author_email="eric.gitonga@example.com",
    description="A tool to visualize files in a directory as 3D animations",
    long_description=open("README.md").read() if __name__ != "__main__" and os.path.exists("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/ericgitonga/3d_file_visualizer",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    install_requires=[
        "numpy>=1.19.0",
        "matplotlib>=3.3.0",
        "imageio>=2.9.0",
        "Pillow>=8.0.0",
        "scipy>=1.5.0",
        "moviepy>=1.0.3",
        "decorator>=4.0.2",
        "imageio-ffmpeg>=0.4.4",
    ],
    entry_points={
        "console_scripts": [
            "3d-visualizer=3d_art:main",
        ],
    },
)
