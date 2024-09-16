from setuptools import setup, find_packages
import re
import ast
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

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
    package_data={
        "": ["*.txt", "*.md", "*.png", "*.pt"],
        "arcjetCV": ["gui/logo/*.png"],
    },
    install_requires=[
        "pyside6",
        "opencv-python",  # OpenCV for image processing
        "matplotlib",  # Plotting library
        "pandas",  # Data analysis library
        "pyarrow",  # Apache Arrow for data serialization
        "scikit-learn",  # Machine learning algorithms
        "segmentation-models-pytorch",  # Deep learning segmentation models
        "torch",  # PyTorch framework
        "torchvision",  # PyTorch vision package
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
