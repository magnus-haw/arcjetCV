from setuptools import setup, find_packages
import sys
import os

# Read the README file for long description
with open("README_pypi.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def check_linux_dependencies():
    if sys.platform.startswith("linux"):
        print("\n[INFO] Linux detected: Checking required system libraries...")

        # List of required packages
        required_packages = [
            "libxcb-xinerama0",
            "libxcb1",
            "libx11-xcb1",
            "libxcb-cursor0",
            "libxcb-icccm4",
            "libxcb-keysyms1",
            "libxcb-render-util0",
            "libxcb-shape0",
            "libxcb-xfixes0",
            "libxcb-randr0",
            "libxcb-util1",
            "libxcb-image0",
            "libxcb-sync1",
            "libxcb-xinput0",
        ]

        try:
            # Check if running on Ubuntu/Debian
            with open("/etc/os-release") as f:
                os_info = f.read().lower()
            if "ubuntu" in os_info or "debian" in os_info:
                print(
                    "\n[INFO] Ubuntu/Debian detected. Installing dependencies via APT..."
                )
                subprocess.run(["sudo", "apt", "update"], check=True)
                subprocess.run(
                    ["sudo", "apt", "install", "-y"] + required_packages, check=True
                )
                print("\n[INFO] System dependencies installed successfully.")
            else:
                print(
                    "\n[WARNING] Non-Debian system detected. Please install the dependencies manually."
                )
                print(
                    "\n[INFO] Run one of the following commands based on your distribution:"
                )
                print(
                    "\n[Ubuntu/Debian] sudo apt-get install "
                    + " ".join(required_packages)
                )
                print("[Fedora] sudo dnf install libxcb libX11-xcb libxcb-cursor")
                print("[Arch] sudo pacman -S libxcb xcb-util xcb-util-cursor\n")

        except Exception as e:
            print(f"\n[ERROR] Could not determine Linux distribution: {e}")


# Run the platform check before proceeding
check_linux_dependencies()

# Define the setup configuration
setup(
    name="arcjetcv",
    version="1.1.3",  # Set the version directly here
    author="arcjetCV team",
    description="Package to process arcjet videos and segment the edge of the shock and of the sample",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/magnus-haw/arcjetCV",
    packages=find_packages(),
    include_package_data=True,  # Include package data based on the rules below
    package_data={
        "": ["*.txt", "*.md", "*.png", "*.gif"],  # Include these file types
        "arcjetCV": [
            "gui/logo/*.png",
            "gui/logo/*.ico",
            "gui/logo/*.icns",
        ],  # Include specific logo images
    },
    exclude_package_data={
        "arcjetCV": [
            "segmentation/contour/Unet-xception_25_original.pt",  # Exclude .pt files
            "segmentation/contour/Unet-xception-last-checkpoint.pt",
            "segmentation/contour/Unet-xception_25_weights_only.pt",
        ],
    },
    install_requires=[
        "pyside6>=6.5.0",  # Ensure compatibility with PySide6 versions
        "opencv-python",
        "opencv-contrib-python",
        "numpy",
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
