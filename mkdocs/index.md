# arcjetCV

![arcjetCV logo](assets/arcjetCV_logo.png){ width="200" }

arcjetCV automates arc jet test video analysis: calibrate the camera, extract shock/material edges, and post-process recession or standoff trajectories. Use it through the desktop GUI or import the Python API for scripted analysis.

## Highlights
- Calibrate cameras with intrinsic + metric steps and export reusable JSON calibration files.
- Apply multiple edge filters (AutoHSV, CNN, HSV, Gray) to extract shock/material contours.
- Post-process with plotting, curve fitting, and CSV/export utilities directly in the GUI.
- Python API mirrors the GUI flow so you can batch-process videos programmatically.
- Built for high-resolution, long-duration footage from arc jet facilities.

## Quick Start
- Install from PyPI: `pip install arcjetCV`
- Launch the GUI after activating your environment: `arcjetCV`
- Prefer conda? Create the provided `env/arcjetCV_env_[cpu/gpu].yml` environment and install in editable mode with `python -m pip install -e .`

## Where to go next
- [Quick Start](quickstart.md) - installation and launch steps for GUI and API.
- [User Manual](user-manual.md) - in-depth walkthrough of calibration, processing, and analysis tabs.
- [Tutorials](tutorials.md) - links to notebooks and Colab for hands-on demos.
- [API & CLI](api.md) - code snippets and guidance for scripting arcjetCV.

## Demo

![arcjetCV processing demo](assets/arcjet_video.gif)
