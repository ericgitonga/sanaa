#!/usr/bin/env python3
"""
3D File Visualizer - Setup Script

This script installs all required dependencies for the 3D File Visualizer.
It checks for the presence of required packages and installs or upgrades them as needed.

First-time users must run this script before running 3d_art.py.

Usage:
    python setup.py install

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
    if missing:
        print(f"Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)
        except subprocess.CalledProcessError as e:
            print(f"Error installing packages: {e}")
            print("You may need to run this script with sudo or use a virtual environment.")
            return False

    # Upgrade packages
    if upgrade:
        print(f"Upgrading packages: {', '.join(upgrade)}")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade"] + upgrade)
        except subprocess.CalledProcessError as e:
            print(f"Error upgrading packages: {e}")
            print("You may need to run this script with sudo or use a virtual environment.")
            return False

    if not missing and not upgrade:
        print("All Python dependencies are already satisfied!")
    else:
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
        return False

    return True


# Run the dependency check and installation when this script is executed directly
if __name__ == "__main__":
    print("3D File Visualizer - Setup")
    print("==========================")
    print("This script will install all required dependencies for the 3D File Visualizer.")
    print("Copyright © 2025 Eric Gitonga - May 16, 2025")
    print()

    success = check_and_install_dependencies()
    if success:
        print("\nSetup complete! All dependencies are installed.")
        print("You can now run the 3D File Visualizer with: python 3d_art.py /path/to/directory")
    else:
        print("\nSetup incomplete. Please install missing dependencies manually.")
        sys.exit(1)

# Setup configuration for packaging
setup(
    name="3d_file_visualizer",
    version="0.1.0",
    author="Eric Gitonga",
    author_email="eric.gitonga@example.com",
    description="A tool to visualize files in a directory as 3D animations",
    long_description=open("README.md").read() if __name__ != "__main__" else "",
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
    ],
    entry_points={
        "console_scripts": [
            "3d-visualizer=3d_art:main",
        ],
    },
)
