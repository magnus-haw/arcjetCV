[![GitHub Docs](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://magnus-haw.github.io/arcjetCV/)
[![PyPI version](https://badge.fury.io/py/arcjetcv.svg)](https://pypi.org/project/arcjetcv/)
[![tutorial](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/magnus-haw/arcjetCV/blob/main/tutorial.ipynb)
[![Downloads](https://pepy.tech/badge/arcjetcv)](https://pepy.tech/project/arcjetcv)
-----

<div align="center">
  <img src="https://github.com/magnus-haw/arcjetCV/blob/main/arcjetCV/gui/logo/arcjetCV_logo_.png" alt="arcjetCV Logo" width="30%">
</div>

# arcjetCV

Package to process arcjet videos and segment the edge of the shock and of the sample.

![arcjetCV Functionality](https://github.com/magnus-haw/arcjetCV/blob/main/docs/source/arcjet_video.gif)

## Installation

### PyPi Installation (Universal)

#### Prerequisites:
- Ensure you have **Python 3.8** or higher installed.

To install **arcjetCV** via **pip** from **PyPi**, run:

```bash
pip install arcjetCV
```

This will install **arcjetCV** along with its dependencies.

#### Note for macOS Users:
You might need to install Xcode Command Line Tools:

```bash
xcode-select --install
```

#### Note for Linux Users:

You may need to install **libxcb-cursor**. Use your package manager to install it:

For **Ubuntu/Debian**-based distributions:
```bash
sudo apt-get install libxcb-cursor0
```

For **Fedora**:
```bash
sudo dnf install libxcb-cursor
```

For **Arch Linux**:
```bash
sudo pacman -S libxcb
```

### Developer Installation

#### Prerequisites:
- A valid **git** installation.
- **Miniconda** or **Anaconda** for environment and package management:
  - [Miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/)
  - [Anaconda](https://docs.anaconda.com/free/anaconda/install/index.html)

To install **arcjetCV** for development purposes, follow these steps:

1. Install `git-lfs`:

   Download and install it from [here](https://git-lfs.github.com/).

2. Clone the repository and install the package:

```bash
git clone https://github.com/magnus-haw/arcjetCV.git
cd arcjetCV
conda env create -f env/arcjetCV_env_[cpu/gpu].yml
conda activate arcjetcv
python -m pip install -e .
```

The `-e` flag stands for 'editable' and means that any changes to the local source code will immediately affect the **arcjetCV** package and GUI.

#### Note for macOS Users:
You might need to install Xcode Command Line Tools:

```bash
xcode-select --install
```

## How to Run

You can now launch the GUI by running:

```bash
conda activate arcjetCV
arcjetCV
```

or you can import arcjetCV's python API inside a python script, e.g. test.py:

```python
import arcjetCV as arcv
video = arcv.Video("tests/arcjet_test.mp4")
```

and then run it as:

```bash
conda activate arcjetCV
python test.py
```

## Citing

If you use arcjetCV in your research, please use the following BibTeX entry to cite [our paper](https://doi.org/10.2514/1.A36132):

```BibTeX
@article{doi:10.2514/1.A36132,
author = {Quintart, Alexandre M. and Haw, Magnus A. and Semeraro, Federico},
title = {arcjetCV: Open-Source Software to Analyze Material Ablation},
journal = {Journal of Spacecraft and Rockets},
volume = {0},
number = {0},
pages = {1-10},
year = {0},
doi = {10.2514/1.A36132},
URL = {https://doi.org/10.2514/1.A36132},
eprint = {https://doi.org/10.2514/1.A36132}
}
```

## Legal / License
Copyright © 2024 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.

Disclaimers

No Warranty: THE SUBJECT SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND, EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR FREEDOM FROM INFRINGEMENT, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL BE ERROR FREE, OR ANY WARRANTY THAT DOCUMENTATION, IF PROVIDED, WILL CONFORM TO THE SUBJECT SOFTWARE. THIS AGREEMENT DOES NOT, IN ANY MANNER, CONSTITUTE AN ENDORSEMENT BY GOVERNMENT AGENCY OR ANY PRIOR RECIPIENT OF ANY RESULTS, RESULTING DESIGNS, HARDWARE, SOFTWARE PRODUCTS OR ANY OTHER APPLICATIONS RESULTING FROM USE OF THE SUBJECT SOFTWARE.  FURTHER, GOVERNMENT AGENCY DISCLAIMS ALL WARRANTIES AND LIABILITIES REGARDING THIRD-PARTY SOFTWARE, IF PRESENT IN THE ORIGINAL SOFTWARE, AND DISTRIBUTES IT "AS IS."

Waiver and Indemnity:  RECIPIENT AGREES TO WAIVE ANY AND ALL CLAIMS AGAINST THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT.  IF RECIPIENT'S USE OF THE SUBJECT SOFTWARE RESULTS IN ANY LIABILITIES, DEMANDS, DAMAGES, EXPENSES OR LOSSES ARISING FROM SUCH USE, INCLUDING ANY DAMAGES FROM PRODUCTS BASED ON, OR RESULTING FROM, RECIPIENT'S USE OF THE SUBJECT SOFTWARE, RECIPIENT SHALL INDEMNIFY AND HOLD HARMLESS THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT, TO THE EXTENT PERMITTED BY LAW.  RECIPIENT'S SOLE REMEDY FOR ANY SUCH MATTER SHALL BE THE IMMEDIATE, UNILATERAL TERMINATION OF THIS AGREEMENT. 
