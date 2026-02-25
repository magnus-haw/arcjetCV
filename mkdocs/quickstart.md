# Quick Start

## Requirements
- Python 3.8+
- For macOS: Xcode Command Line Tools (`xcode-select --install`)
- For Linux: `libxcb-cursor` (`sudo apt-get install libxcb-cursor0` on Debian/Ubuntu)

## Install from PyPI (recommended)
```bash
pip install arcjetCV
```

## Developer install
```bash
# 1) Clone and set up the conda environment (CPU or GPU variants available)
git clone https://github.com/magnus-haw/arcjetCV.git
cd arcjetCV
conda env create -f env/arcjetCV_env_[cpu/gpu].yml
conda activate arcjetcv

# 2) Install in editable mode
python -m pip install -e .
```

## Launch the GUI
```bash
# Activate your environment first if using conda
conda activate arcjetcv
arcjetCV
```

## Use the Python API
```python
import arcjetCV as arcv
video = arcv.Video("tests/arcjet_test.mp4")
# Continue with processing just like the GUI pipeline
```

Run the script with your environment active:
```bash
python your_script.py
```
