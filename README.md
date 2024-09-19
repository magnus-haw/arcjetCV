[![Documentation Status](https://readthedocs.org/projects/arcjetcv/badge/?version=latest)](https://arcjetcv.readthedocs.io/en/latest/?badge=latest)
[![Anaconda-Server Badge](https://anaconda.org/conda-forge/arcjetcv/badges/version.svg)](https://anaconda.org/conda-forge/arcjetcv)
[![tutorial](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/magnus-haw/arcjetCV/blob/main/tutorial.ipynb)

-----

<div align="center">
  <img src="https://raw.githubusercontent.com/magnus-haw/arcjetCV/main/arcjetCV/gui/logo/arcjetCV_logo_.png" alt="arcjetCV Logo" width="30%">

</div>

# arcjetCV

Package to process arcjet videos and segment the edge of the shock and of the sample.

![arcjetCV Functionality](https://i.imgur.com/YOUR_IMAGE_ID.gif)


## Installation

### Prerequisites
The installation of the arcjetCV GUI and python package require a valid git installation, installation of the git-lfs [(git large file storage)](https://git-lfs.github.com/) add-on and a 
[Miniconda](https://docs.anaconda.com/free/miniconda/miniconda-install/) or
[Anaconda](https://docs.anaconda.com/free/anaconda/install/index.html) installation. 

### Unix Users

The software can be installed by running:

```bash
conda create --name arcjetcv conda-forge::arcjetcv
```
#### Note for macOS Users:


Please ensure that you have the Xcode Command Line Tools installed:

```bash
xcode-select --install
```

### Windows Users and Developers

For local development of arcjetCV and for Windows users, these are the recommended installation steps:

1. **Install `git lfs` (Git Large File Storage):**

   You can download and install it from [here](https://git-lfs.github.com/).

2. **Clone the repository and install the package:**

```bash
git clone https://github.com/magnus-haw/arcjetCV.git
cd arcjetCV
conda env create -f env/arcjetCV_env_[cpu/gpu].yml
conda activate arcjetCV
python -m pip install -e . 
```

The -e flag stands for 'editable' and it means that any change to the local source code will have immediate effect on the arcjetCV python package and GUI.

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

If you use arcjetCV in your research, please use the following BibTeX entry to cite [our paper](https://arxiv.org/abs/2404.11492):

```BibTeX
@article{arcjetCV,
  title={arcjetCV: an open-source software to analyze material ablation},
  author={Quintart, Alexandre and Haw, Magnus and Semeraro, Federico},
  journal={arXiv preprint arXiv:2404.11492},
  year={2024}
}
```

## Legal / License
Copyright © 2024 United States Government as represented by the Administrator of the National Aeronautics and Space Administration.  All Rights Reserved.

Disclaimers

No Warranty: THE SUBJECT SOFTWARE IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND, EITHER EXPRESSED, IMPLIED, OR STATUTORY, INCLUDING, BUT NOT LIMITED TO, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL CONFORM TO SPECIFICATIONS, ANY IMPLIED WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, OR FREEDOM FROM INFRINGEMENT, ANY WARRANTY THAT THE SUBJECT SOFTWARE WILL BE ERROR FREE, OR ANY WARRANTY THAT DOCUMENTATION, IF PROVIDED, WILL CONFORM TO THE SUBJECT SOFTWARE. THIS AGREEMENT DOES NOT, IN ANY MANNER, CONSTITUTE AN ENDORSEMENT BY GOVERNMENT AGENCY OR ANY PRIOR RECIPIENT OF ANY RESULTS, RESULTING DESIGNS, HARDWARE, SOFTWARE PRODUCTS OR ANY OTHER APPLICATIONS RESULTING FROM USE OF THE SUBJECT SOFTWARE.  FURTHER, GOVERNMENT AGENCY DISCLAIMS ALL WARRANTIES AND LIABILITIES REGARDING THIRD-PARTY SOFTWARE, IF PRESENT IN THE ORIGINAL SOFTWARE, AND DISTRIBUTES IT "AS IS."

Waiver and Indemnity:  RECIPIENT AGREES TO WAIVE ANY AND ALL CLAIMS AGAINST THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT.  IF RECIPIENT'S USE OF THE SUBJECT SOFTWARE RESULTS IN ANY LIABILITIES, DEMANDS, DAMAGES, EXPENSES OR LOSSES ARISING FROM SUCH USE, INCLUDING ANY DAMAGES FROM PRODUCTS BASED ON, OR RESULTING FROM, RECIPIENT'S USE OF THE SUBJECT SOFTWARE, RECIPIENT SHALL INDEMNIFY AND HOLD HARMLESS THE UNITED STATES GOVERNMENT, ITS CONTRACTORS AND SUBCONTRACTORS, AS WELL AS ANY PRIOR RECIPIENT, TO THE EXTENT PERMITTED BY LAW.  RECIPIENT'S SOLE REMEDY FOR ANY SUCH MATTER SHALL BE THE IMMEDIATE, UNILATERAL TERMINATION OF THIS AGREEMENT. 
