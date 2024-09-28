from setuptools import setup, find_packages

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define the setup configuration
setup(
    name="arcjetCV",
    version="0.0.4.dev5",  # Set the version directly here
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
