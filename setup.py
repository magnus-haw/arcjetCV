from setuptools import setup, find_packages
import re
import ast

# Read the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Extract version number from the package
_version_re = re.compile(r"__version__\s+=\s+(.*)")
with open("arcjetCV/__init__.py", "rb") as f:
    version = str(
        ast.literal_eval(_version_re.search(f.read().decode("utf-8")).group(1))
    )

setup(
    name="arcjetCV",
    version=version,
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
        "pyside6",
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
