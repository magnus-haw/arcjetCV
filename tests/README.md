
# arcjetCV Tests

This folder contains the tests for the arcjetCV functions and GUI.

## Installation

After installing arcjetCV (see [README.md](../README.md)), install these extra packages:

```bash
conda activate arcjetcv
conda install -c conda-forge pytest pytest-qt pytest-mock
```

# How to use

Tests can be run singularly using e.g.:

```bash
cd tests
pytest test_gui.py
```

or in bulk using:

```bash
cd tests
pytest
```
