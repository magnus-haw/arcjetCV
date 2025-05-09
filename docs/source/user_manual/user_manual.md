<!-- # Introduction

Arcjet Computer Vision (```arcjetCV```) is a software application built to automate analysis of arc jet ground test video footage. This includes tracking material recession, sting arm motion, and the shock-material standoff distance. Consequently, ArcjetCV provides a new capability to resolve and validate new physics associated with non-linear processes. This is an essential step to reduce testing, modeling, and validation uncertainties for heatshield material performance.

Arc jets are plasma wind tunnels used to test the performance of heatshield materials for spacecraft atmospheric entry. These facilities present an extremely harsh flow environment with heat fluxes up to 109 W/$m^2$ for up to 30 minutes. The plasma is low-temperature ($\sim1$ eV) but high pressure ($>$ 10 kPa) creating high-enthalpy supersonic flows similar to atmospheric entry conditions. Typically, material samples are measured before and after a test to characterize the total recession. However, this does not capture time-dependent effects such as material expansion and non-linear recession.

Since manual segmentation is onerous, very few time-resolved measurements of material recession/expansion/shrinkage under arcjet test conditions exist. ArcjetCV seeks to automate these measurements such that time-resolved material behavior can be extracted for every arc jet test.

ArcjetCV makes new time-resolved measurements of material recession, expansion new analysis of arcjet test videos which measure both the time-dependent 2D recession of the material samples and the shock standoff distance. The results show non-linear time-dependent effects are present for some conditions. The material and shock edges are extracted from the videos by training and applying a convolutional neural network. Due to the consistent camera settings, the machine learning model achieves high accuracy ($\pm$ 2 px) relative to manually segmented images with only a small number of training frames.
 -->

Introduction
============================================

The graphical user interface of arcjetCV is divided into two parts: the "Extract Edges" processing tab and the "Analysis" post-processing tab. These tabs are responsible for processing the video and post-processing the extracted edges, respectively.

Calibration
============================================

The **Calibrate** tab enables camera correction and physical scaling. It is divided into two panels: **Intrinsic Calibration** and **Metric Calibration**.

### Intrinsic Calibration

This step calculates the camera's intrinsic parameters, including focal length, principal point, and distortion coefficients, using a known calibration pattern.

1. **Print Chessboard**

   Click the "Print Chessboard" button to generate and print a pattern (default: 4 columns × 9 rows of internal corners).

2. **Set Pattern Size**

   Define the number of internal corners in the chessboard (e.g., Cols: 4, Rows: 9).

3. **Load Calibration Images**

   Load one or more images that clearly show the calibration pattern under test conditions.

4. **Calibrate Camera**

   Press "Calibrate Camera" to compute the intrinsic matrix and distortion coefficients.

---

### Metric Calibration

This defines the conversion factor between pixels and physical dimensions (e.g., mm), necessary for accurate recession or displacement measurements.

You can choose between:

- **Pattern Resolution** (recommended)
- **Ruler Resolution** (using known-length features)

#### Steps (Pattern Resolution):

1. **Set Pattern Size**

   Must match the one used during intrinsic calibration (e.g., Cols: 4, Rows: 9).

2. **Load Image for Resolution Measurement**

   Load a still image taken under test conditions that includes the same pattern.

3. **Enter Diagonal Distance**

   Input the real-world diagonal distance of the pattern in millimeters.

4. **Calculate Resolution**

   Click the "Calculate Resolution" button to compute the scaling factor (e.g., mm/pixel), which will be used in the **Analyze** tab.

---

### Save Calibration

Click **Save Calibration** to export both intrinsic and metric parameters to a `.json` file. This file can be reused for distortion correction and accurate plotting in later analysis.

Processing
============================================

The process involves several steps:

1. **Load Video**

   Click on the "Load Video" button on the top right of the right panel and locate a suitable file. Supported file types are .mp4, .avi, .mov, and .m4v. It is recommended to process larger files (greater than 500 MB) on a powerful machine with a suitable GPU.

2. **Review Processing Parameters**

   After loading the video, arcjetCV will estimate values for the start/end frame indices, flow direction, and region of interest (ROI). Adjust these as necessary.

   * **Set Flow Direction**

     Choose the flow direction to determine which side of the material sample is the leading edge (LEFT, RIGHT, UP, DOWN).

   * **Set Start/End Frames**

     Define the starting and ending frames in the "Output Parameters" section. These frames are indicated by vertical green lines on the intensity bar plot.

   * **Setting the Region of Interest (ROI)**

     The ROI is represented as a white rectangle and should be applicable for both the start and end frames. The minimum area for the ROI should be at least 40 pixels by 40 pixels.

3. **Select Edge Filter**

   Choose from one of the four filter modes: AutoHSV, CNN, HSV, Gray. The chosen filter will be applied to the current video frame displayed on the left side of the window.

4. **Test Filter Performance**

   Evaluate the filter's performance at various points throughout the video.

5. **Process Frames**

   Select a frame range for processing and click the "Process All" button. This will generate an output file with the edge data and a meta file with the processing settings.

6. **Process in Several Steps**

   If needed, the video can be processed in multiple steps using different filters.

Edge Filters
------------

ArcjetCV provides several edge filter options:

* **AutoHSV**

  Utilizes a pre-defined union of multiple HSV ranges to find contours.

* **CNN**

  Employs a convolutional neural network trained on various frames.

* **HSV**

  Finds contours within manually specified HSV ranges.

* **Gray**

  Detects objects based on the grayscale of the frame.

Post-Processing
============================================

The **Analyze** tab contains tools for visualizing and fitting the processed edge data. The primary functions include loading, plotting, fitting edge data, and exporting post-processed data.

1. **Load Processed Edges**

   Load the processed data files created in the processing tab.

2. **Plot Data**

   Use the "Plot Data" button to visualize the edge data in the top two plotting windows.

3. **Input Units/Scale**

   The data in the top right plot is scaled based on the input parameters specified in the "Plotting Parameters" sub-tab.

4. **Fit Data**

   Once data is plotted, you can apply fitting functions by setting several parameters in the "Fitting Parameters" sub-tab.

5. **Export**

   Export the plotted and fitted data to CSV using the "Export CSV/Plots" button.

