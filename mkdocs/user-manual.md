# User Manual

The arcjetCV GUI is split into two parts: **Extract Edges** (processing) and **Analyze** (post-processing). Use the steps below to calibrate the camera, process video frames, and export results.

## Calibration

### Intrinsic Calibration
Compute the intrinsic matrix and distortion coefficients from a chessboard pattern.
1. Click **Print Chessboard** to generate a pattern (default: 4 columns x 9 rows of internal corners).
2. Set **Pattern Size** to match your printed pattern (e.g., Cols: 4, Rows: 9).
3. Load one or more images that clearly show the chessboard under test conditions.
4. Press **Calibrate Camera** to solve for focal length, principal point, and distortion terms.

### Metric Calibration
Define the conversion factor between pixels and physical dimensions.
- Use **Pattern Resolution** (recommended) or **Ruler Resolution** (known-length features).
- Steps (Pattern Resolution):
  1. Set **Pattern Size** to match the intrinsic calibration.
  2. Load a still image that includes the pattern.
  3. Enter the real-world diagonal distance of the pattern (mm).
  4. Click **Calculate Resolution** to compute mm/pixel for later analysis.

### Save Calibration
Export intrinsic and metric parameters to a `.json` file with **Save Calibration**. Reuse it for distortion correction and accurate plotting.

## Processing
1. **Load Video**: choose .mp4/.avi/.mov/.m4v files. For >500 MB, a machine with a good GPU is recommended.
2. **Review Parameters**: adjust flow direction, frame range, and ROI. The start/end frames appear as green lines on the intensity plot; the ROI is a white rectangle (minimum ~40x40 px).
3. **Select Edge Filter**: pick **AutoHSV**, **CNN**, **HSV**, or **Gray**. The filtered frame appears on the left.
4. **Test Filters**: spot-check filter performance at several timestamps.
5. **Process Frames**: choose a frame range and click **Process All**. Outputs include an edge file and a meta file with settings.
6. **Process in Steps**: you can process multiple ranges with different filters if needed.

## Edge Filters
- **AutoHSV**: predefined union of HSV ranges to find contours.
- **CNN**: convolutional neural network trained on representative frames.
- **HSV**: manual HSV ranges to isolate edges.
- **Gray**: grayscale-based object detection.

## Post-Processing
1. **Load Processed Edges** produced by the processing tab.
2. **Plot Data** in the top plots; configure units and scale in **Plotting Parameters**.
3. **Fit Data** by setting options in **Fitting Parameters** once curves are plotted.
4. **Export** plots and fitted data as CSV with **Export CSV/Plots**.
