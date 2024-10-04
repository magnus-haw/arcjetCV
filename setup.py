from setuptools import setup, find_packages
import sys
import os

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define a function to check for platform-specific dependencies
def check_linux_dependencies():
    if sys.platform.startswith('linux'):
        print("\n[INFO] Linux detected: Ensure the following system libraries are installed:")
        print("\n[INFO] Run the following command to install the necessary Qt dependencies:")
        print("\n[Ubuntu/Debian] sudo apt-get install libxcb-xinerama0 libxcb1 libx11-xcb1 libxcb-cursor0")
        print("[Fedora] sudo dnf install libxcb libX11-xcb libxcb-cursor")
        print("[Arch] sudo pacman -S libxcb xcb-util xcb-util-cursor\n")

# Run the platform check before proceeding
check_linux_dependencies()

# Define the setup configuration
setup(
    name="arcjetCV",
    version="0.0.4.dev8",  # Set the version directly here
    author="arcjetCV team",
    description="Package to process arcjet videos and segment the edge of the shock and of the sample",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/magnus-haw/arcjetCV",
    packages=find_packages(),
    include_package_data=True,  # Include package data based on the rules below
    package_data={
        "": ["*.txt", "*.md", "*.png", "*.gif"],  # Include these file types
        "arcjetCV": ["gui/logo/*.png"],  # Include specific logo images
    },
    exclude_package_data={
        "arcjetCV": [
            "segmentation/contour/Unet-xception_25_original.pt",  # Exclude .pt files
            "segmentation/contour/Unet-xception-last-checkpoint.pt",
        ],
    },
    install_requires=[
        "pyside6>=6.5.0",  # Ensure compatibility with PySide6 versions
        "opencv-python",
        "matplotlib",
        "pandas",
        "pyarrow",
        "scikit-learn",
        "segmentation-models-pytorch",
        "torch",
        "torchvision",
    ],
    entry_points={
        "console_scripts": [
            "arcjetCV=arcjetCV.gui.main:main",
            "arcjetcv=arcjetCV.gui.main:main",
        ],
    },
    project_urls={
        "Bug Tracker": "https://github.com/magnus-haw/arcjetCV/issues",
    },
    platforms=["Linux", "Mac", "Windows"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Physics",
    ],
)