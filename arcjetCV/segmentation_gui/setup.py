from setuptools import setup, find_packages

setup(
    name="SegmentationGUI",
    version="0.1.0",
    author="Your Name",
    author_email="alex@flying-squirrel.space",
    description="A GUI for image segmentation.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/alexandrequ/segmentation_gui",  # Adjust this to your repository
    packages=find_packages(),
    install_requires=[
        "PySide6",
        "opencv-python",
        "numpy",
        "torch",
        "torchvision",
        "matplotlib",
        # Add other dependencies as needed
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
    ],
    python_requires=">=3.7",
    entry_points={
        "console_scripts": [
            "segmentation_gui=segmentation_gui.main_window:main",
        ],
    },
    include_package_data=True,
    package_data={
        "segmentation_gui": ["*.ui"]
    },  # If you have .ui files or other resources
)
