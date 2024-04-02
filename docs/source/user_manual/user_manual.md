# Using arcjetCV: The Graphical User Interface

The graphical user interface (GUI) of arcjetCV is divided into two main tabs: "Extract Edges" for processing and "Analysis" for post-processing. These tabs enable users to process videos to extract edges and then analyze these extracted edges, respectively.

## Processing

![Video processing tab showing edge detection for individual frames, including settings for edge filters, start/stop indices, and flow direction.](GUI1.png)

1. **Load Video:** Begin by loading a video file through the "Load Video" button located at the top right of the right panel. Supported file formats include *.mp4, *.avi, *.mov, and *.m4v. While there are no strict restrictions on file size or length, processing large files (>500 MB) is recommended on a powerful machine equipped with a suitable GPU.

2. **Review Processing Parameters:** Upon loading a video, arcjetCV attempts to auto-guess the start/end frame indices, flow direction, and the region of interest (ROI). Adjust these parameters as necessary:
    - **Set Flow Direction:** Determines the flow direction, affecting which side of the material sample is considered the leading edge. Options include LEFT, RIGHT, UP, DOWN.
    - **Set Start/End Frames:** Define the starting and ending frames in the "Output Parameters" section. These frames are marked by vertical green lines on the intensity bar plot below the main video window, with the current frame indicated by a vertical red line.
    - **Set the Region of Interest (ROI):** The ROI, visualized as a white rectangle, can be adjusted by clicking and dragging on the video frame. Only the section within the ROI will be processed. Ensure the ROI is suitable for both the start and end frames, encompasses at least 40x40 pixels, and includes both the sample edge and any potential shock presence.

3. **Select Edge Filter:** Choose an edge detection filter from the available options: AutoHSV, CNN, HSV, and Gray. The effect of the selected filter is displayed in real-time on the video frame.

4. **Test Filter Performance:** To ensure reliable edge detection, test the filter at various points throughout the video—beginning, middle, and end. This approach helps accommodate changes in camera settings, sample color, or brightness over time.

5. **Process Frames:** After setting the frame range and selecting a filter, click "Process All" to begin processing. This generates an output file with edge data and a settings meta file in the video's directory. Optionally, an annotated video can also be exported.

6. **Multiple Steps Processing:** For complex cases, processing the video in sections with different filters may be necessary. The "Analysis" tab supports loading and analyzing data from multiple processed files.

### Edge Filters

- **AutoHSV:** Utilizes a predefined union of multiple HSV ranges for contour detection, transforming BGR to HSV for enhanced contrast.
- **CNN:** Employs a convolutional neural network trained on various frames for precise edge extraction. While accurate, it is slower (~1 second per frame) than other methods.
- **HSV:** Finds contours within manually specified HSV ranges, also leveraging BGR-HSV transformation.
- **Gray:** Detects objects based on the grayscale intensity, ideal for bright sample edges but less effective for shock detection.

## Post-processing

The "Analyze" tab includes tools for visualizing, fitting, and exporting processed edge data. Functions include loading edge data, plotting, fitting to models, and exporting results.

1. **Load Processed Edges:** Load edge data files (*.json) generated during processing. Multiple files from different video sections can be loaded simultaneously.

2. **Plot Data:** Visualizes XY edge traces and time-dependent quantities extracted from edges. Selectable metrics and interactive plot features are available for detailed analysis.

3. **Input Units/Scale:** Adjust plot scales based on material sample diameter and video frame rate. Modifying these parameters requires re-plotting and re-exporting data to reflect changes.

4. **Fit Data:** Apply fitting functions to plotted data. Fitting parameters can be adjusted in the "Fitting Parameters" sub-tab.

5. **Export Data:** Results can be exported to CSV, including time series data and fitting parameters. Plots are also saved automatically.

Additional information and statistics about the processed data are displayed in the "Data Summary" section.

![Post-processing window showcasing the analysis tools and features available in arcjetCV.](GUI3.png)
