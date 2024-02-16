# Import necessary libraries
import os, sys
from pathlib import Path
import numpy as np
import pandas as pd
import cv2 as cv
import json
from numbers import Number

# Import PySide modules for the GUI
from arcjetCV.gui.arcjetCV_gui import Ui_MainWindow
from PySide6 import QtWidgets
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap, QIcon

# Import custom analysis functions
from arcjetCV.utils.utils import (
    splitfn,
    getOutlierMask,
    annotateImage,
    WorkerThread,
    annotate_image_with_frame_number,
    CLAHE_normalize,
)
from arcjetCV.utils.video import Video, VideoMetaJSON
from arcjetCV.utils.output import OutputListJSON
from arcjetCV.utils.processor import ArcjetProcessor
from arcjetCV.segmentation.time.time_segmentation import (
    time_segmentation,
    extract_interest,
)
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
from matplotlib.widgets import RectangleSelector


class MainWindow(QtWidgets.QMainWindow):
    frame_processed = Signal()

    # class constructor
    def __init__(self):
        """
        Constructor for the MainWindow class.

        This class represents the main window of the application.

        Attributes:
            - frame_processed: Signal emitted when a frame is processed.

        """
        super().__init__()

        # Initialize the user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Set the application icon
        icon_path = "gui/logo/arcjetCV_logo_white.png"  # Replace with the actual path to your icon file
        icon = QIcon(icon_path)
        self.setWindowIcon(icon)

        # Initialize class variables and flags
        self.stop = False
        self.homedir = Path(__file__).parent.absolute()
        self.initial_dir = "ok"

        # Load and process the application logo
        self.frame = cv.imread(
            str(self.homedir.joinpath(Path("gui/logo/arcjetCV_logo_white.png")))
        )
        self.rgb_frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)

        # Initialize frame and plotting windows
        self.imgdata = self.rgb_frame
        self.h, self.w, self.chan = np.shape(self.frame)
        self._plot_ref = None
        self._tplot_ref = None
        self._brightness_ref = None
        self.clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(9, 9))
        self.show_img()

        # Initialize line start and stop positions
        self.start_line = None
        self.stop_line = None

        # Flags for video loading and processing
        self.VIDEO_LOADED = False
        self.NEW_VIDEO = False

        # Initialize folder/file properties
        self.folder = None
        self.path = None
        self.filename = None
        self.ext = None
        self.video = None
        self.videometa = None

        # Processor objects
        self.processor = None
        self.cnn = None

        # Data structures
        self.raw_outputs = []
        self.time_series = None
        self.PLOTKEYS = []
        self.fit_dict = None
        self._plot_ref = None

        # Connect interface buttons to their respective functions
        self.ui.pushButton_process.clicked.connect(self.process_all)
        self.ui.pushButton_loadVideo.clicked.connect(self.load_video)
        self.ui.pushButton_export_csv.clicked.connect(self.export_to_csv)
        self.ui.pushButton_fitData.clicked.connect(self.fit_data)
        self.ui.pushButton_LoadFiles.clicked.connect(self.load_outputs)
        self.ui.pushButton_PlotData.clicked.connect(self.plot_outputs)
        self.ui.checkBox_display_shock2.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_m75_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_m25_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_model_center.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_25_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_75_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_shock_area.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_model_rad.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_shock_center.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_shockmodel.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_ypos.stateChanged.connect(self.plot_outputs)

        self.ui.applyCrop.clicked.connect(self.update_crop)
        self.ui.comboBox_units.setCurrentText("[mm]")
        self.init_plot_brightness()

        # Set some UI elements to be initially disabled
        self.ui.spinBox_FrameIndex.setDisabled(True)
        self.ui.comboBox_flowDirection.setDisabled(True)
        self.ui.comboBox_filterType.setDisabled(True)
        self.ui.FilterTabs.setDisabled(True)
        self.ui.comboBox_filterType.setDisabled(True)
        self.ui.comboBox_filterType.setDisabled(True)

        # Show the main window
        self.show()

    def show_img(self):
        """
        Displays an image from the `self.rgb_frame` attribute on the UI canvas.

        This function updates the UI canvas with the current image stored in `self.rgb_frame`.

        Returns:
            None

        """
        self.imgdata = self.rgb_frame

        if self._plot_ref is None:

            # Create a new plot reference and define the cursor data format
            plot_refs = self.ui.label_img.canvas.axes.imshow(
                self.imgdata, aspect="equal"
            )

            plot_refs.axes.get_xaxis().set_visible(False)
            plot_refs.axes.get_yaxis().set_visible(False)
            # Customize axis spines color to match the background (hiding the border)
            plot_refs.axes.spines["top"].set_color("none")
            plot_refs.axes.spines["bottom"].set_color("none")
            plot_refs.axes.spines["left"].set_color("none")
            plot_refs.axes.spines["right"].set_color("none")

            def format_cursor_data(data):
                """
                Return a string representation of cursor data.

                This function formats the cursor data to display RGB and HSV values.

                Args:
                    data (list): Cursor data containing RGB values.

                Returns:
                    str: Formatted string containing RGB and HSV values.

                """
                try:
                    data[0]
                except (TypeError, IndexError):
                    data = [data]
                data_str = "RGB = [" + ", ".join(
                    "{:0.3g}".format(item) for item in data if isinstance(item, Number)
                )
                hsv = rgb_to_hsv(np.array(data) / 255.0)
                hsv_str = (
                    "HSV = ["
                    + "%i " % (hsv[0] * 180)
                    + ","
                    + "%i " % (hsv[1] * 255)
                    + ","
                    + "%i " % (hsv[2] * 255)
                    + "]"
                )
                return data_str + "] " + hsv_str

            plot_refs.format_cursor_data = format_cursor_data
            self._plot_ref = plot_refs

            # Add the RectangleSelector to the canvas axes
            self.rect_selector = RectangleSelector(self._plot_ref.axes, self.onselect)

        else:
            # Update the existing plot reference with new image data
            self._plot_ref.set_data(self.imgdata)

        # Trigger the canvas to update and redraw.
        self.ui.label_img.canvas.draw()

    # Define a function to be called when the rectangle is drawn
    def onselect(self, eclick, erelease):
        global rectangle

        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata

        # Set the values for spin boxes
        self.ui.spinBox_crop_xmin.setValue(x1)
        self.ui.spinBox_crop_xmax.setValue(x2)
        self.ui.spinBox_crop_ymin.setValue(y1)
        self.ui.spinBox_crop_ymax.setValue(y2)
        self.update_crop()

    def update_crop(self):
        """Update the crop area"""

        # Validate bounding box inputs here
        if (
            self.ui.spinBox_crop_xmax.value() - self.ui.spinBox_crop_xmin.value() >= 40
            and self.ui.spinBox_crop_ymax.value() - self.ui.spinBox_crop_ymin.value()
            >= 40
        ):
            self.videometa["XMIN"] = self.ui.spinBox_crop_xmin.value()
            self.videometa["XMAX"] = self.ui.spinBox_crop_xmax.value()
            self.videometa["YMIN"] = self.ui.spinBox_crop_ymin.value()
            self.videometa["YMAX"] = self.ui.spinBox_crop_ymax.value()
            self.videometa.write()
            self.update_frame_index()
        else:
            msg = QMessageBox()
            msg.setWindowTitle("ArcjetCV Warning")
            msg.setText(
                "Please check your crop values : The minimum crop size allowed is 40x40"
            )
            msg.setIconPixmap(QPixmap("gui/logo/arcjetCV_logo.png"))
            x = msg.exec_()

    def brightness_click_slot(self, x, y):
        # Slot to handle the custom signal emitted by the Matplotlib widget
        # print(f"Mouse clicked at (x={x}, y={y})")
        try:
            if x > 0 and x < self.video.nframes - 1:
                self.ui.spinBox_FrameIndex.setValue(int(x))
        except:
            pass

    def update_frame_index(self):

        if self.NEW_VIDEO == True:
            self.ui.spinBox_crop_xmin.setValue(self.videometa["XMIN"])
            self.ui.spinBox_crop_xmax.setValue(self.videometa["XMAX"])
            self.ui.spinBox_crop_ymin.setValue(self.videometa["YMIN"])
            self.ui.spinBox_crop_ymax.setValue(self.videometa["YMAX"])

        self.ui.maxHue.setDisabled(False)
        self.ui.minHue.setDisabled(False)
        self.ui.minIntensity.setDisabled(False)
        self.ui.maxIntensity.setDisabled(False)
        self.ui.minSaturation.setDisabled(False)
        self.ui.maxSaturation.setDisabled(False)

        self.ui.maxHue_2.setDisabled(False)
        self.ui.minHue_2.setDisabled(False)
        self.ui.minIntensity_2.setDisabled(False)
        self.ui.maxIntensity_2.setDisabled(False)
        self.ui.minSaturation_2.setDisabled(False)
        self.ui.maxSaturation_2.setDisabled(False)

        if (
            self.ui.comboBox_filterType.currentText() == "CNN"
            or self.ui.comboBox_filterType.currentText() == "AutoHSV"
        ):  # disabled the tabs with CNN
            self.ui.tab_3.setDisabled(True)
            self.ui.tab_4.setDisabled(True)
        elif self.ui.comboBox_filterType.currentText() == "GRAY":
            self.ui.tab_3.setDisabled(False)
            self.ui.tab_4.setDisabled(False)
            self.ui.maxHue.setDisabled(True)
            self.ui.minHue.setDisabled(True)
            self.ui.minIntensity.setDisabled(False)
            self.ui.maxIntensity.setDisabled(False)
            self.ui.minSaturation.setDisabled(True)
            self.ui.maxSaturation.setDisabled(True)

            self.ui.maxHue_2.setDisabled(True)
            self.ui.minHue_2.setDisabled(True)
            self.ui.minIntensity_2.setDisabled(False)
            self.ui.maxIntensity_2.setDisabled(False)
            self.ui.minSaturation_2.setDisabled(True)
            self.ui.maxSaturation_2.setDisabled(True)

        else:
            self.ui.tab_3.setDisabled(False)
            self.ui.tab_4.setDisabled(False)

        frame_index = self.ui.spinBox_FrameIndex.value()
        frame = self.video.get_frame(frame_index)

        # Prepare filter parameter dict
        if frame is None:
            return
        inputdict = {"SEGMENT_METHOD": str(self.ui.comboBox_filterType.currentText())}
        inputdict["HSV_MODEL_RANGE"] = [
            (
                self.ui.minHue.value(),
                self.ui.minSaturation.value(),
                self.ui.minIntensity.value(),
            ),
            (
                self.ui.maxHue.value(),
                self.ui.maxSaturation.value(),
                self.ui.maxIntensity.value(),
            ),
        ]
        inputdict["HSV_SHOCK_RANGE"] = [
            (
                self.ui.minHue_2.value(),
                self.ui.minSaturation_2.value(),
                self.ui.minIntensity_2.value(),
            ),
            (
                self.ui.maxHue_2.value(),
                self.ui.maxSaturation_2.value(),
                self.ui.maxIntensity_2.value(),
            ),
        ]
        inputdict["THRESHOLD"] = self.ui.minIntensity.value()
        inputdict["FLOW_DIRECTION"] = self.ui.comboBox_flowDirection.currentText()
        self.processor.FLOW_DIRECTION = self.ui.comboBox_flowDirection.currentText()

        crop_range = [
            [self.ui.spinBox_crop_ymin.value(), self.ui.spinBox_crop_ymax.value()],
            [self.ui.spinBox_crop_xmin.value(), self.ui.spinBox_crop_xmax.value()],
        ]

        # Apply crop params
        if self.processor.CROP != crop_range:
            self.processor.set_crop(crop_range)
            if (
                self.VIDEO_LOADED
            ):  # To avoid crash (can be applied to all the function update_frame)
                self.videometa["YMIN"] = self.ui.spinBox_crop_ymin.value()
                self.videometa["XMIN"] = self.ui.spinBox_crop_xmin.value()
                self.videometa["YMAX"] = self.ui.spinBox_crop_ymax.value()
                self.videometa["XMAX"] = self.ui.spinBox_crop_xmax.value()
                self.videometa.write()

        # Normalize input frame crop window
        try:
            if self.processor.CHANNELS == 1:
                crop_ = frame[
                    crop_range[0][0] : crop_range[0][1],
                    crop_range[1][0] : crop_range[1][1],
                ]
                frame[
                    crop_range[0][0] : crop_range[0][1],
                    crop_range[1][0] : crop_range[1][1],
                ] = CLAHE_normalize(crop_, self.clahe)
            else:
                crop_ = frame[
                    crop_range[0][0] : crop_range[0][1],
                    crop_range[1][0] : crop_range[1][1],
                    :,
                ]
                frame[
                    crop_range[0][0] : crop_range[0][1],
                    crop_range[1][0] : crop_range[1][1],
                    :,
                ] = CLAHE_normalize(crop_, self.clahe)
        except IndexError:
            pass

        # Process frame
        contour_dict, argdict = self.processor.process(frame, inputdict)

        # Draw contours
        for key in contour_dict.keys():
            if key == "MODEL":
                cv.drawContours(frame, contour_dict[key], -1, (0, 255, 0), 2)
            elif key == "SHOCK" and self.ui.checkbox_display_shock.isChecked():
                cv.drawContours(frame, contour_dict[key], -1, (0, 0, 255), 2)

        # Draw annotations
        annotate_image_with_frame_number(frame, frame_index)
        if self.ui.checkBox_annotate.isChecked():
            annotateImage(frame, argdict, top=True, left=True)

        # Draw Crop box
        start_point = (self.processor.CROP[1][0], self.processor.CROP[0][0])
        end_point = (self.processor.CROP[1][1], self.processor.CROP[0][1])

        if self.ui.checkBox_crop.isChecked():
            cv.rectangle(frame, start_point, end_point, (255, 255, 255), 2)

        # Remove local objects
        self.frame = frame.copy()
        del frame
        self.rgb_frame = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        self.frame_processed.emit()
        self.plot_location()

    def load_video(self):
        """Loads a single video file using dialog"""

        print("------New Video-----")
        # create fileDialog to select file
        dialog = QtWidgets.QFileDialog()
        options = QtWidgets.QFileDialog.Options()
        pathmask = dialog.getOpenFileName(
            None,
            "Select Video",
            "",
            "Video Files (*.mp4 	*.avi *.mov *.m4v);;All Files (*)",
            options=options,
        )
        self.NEW_VIDEO = True

        self.path = pathmask[0]
        self._plot_ref = None
        if self.path != "":
            self.folder, self.filename, self.ext = splitfn(self.path)

            self.ui.spinBox_FrameIndex.setDisabled(False)
            self.ui.comboBox_flowDirection.setDisabled(False)
            self.ui.comboBox_filterType.setDisabled(False)
            self.ui.FilterTabs.setDisabled(False)
            self.ui.comboBox_filterType.setDisabled(False)
            self.ui.comboBox_filterType.setDisabled(False)
            self.ui.label_img.canvas.axes.clear()
            self.ui.label_img.canvas.draw()

            # Create video object
            try:
                self.video = Video(self.path)
                self.videometa = VideoMetaJSON(
                    os.path.join(self.folder, self.filename + ".meta")
                )
                self.w = self.video.w
                self.h = self.video.h
                print("##################  Nframes: ", self.video.nframes)
                # Infer meta parameters
                if (
                    self.videometa["FIRST_GOOD_FRAME"] is None
                    or self.videometa["HEIGHT"] is None
                ):
                    self.videometa["WIDTH"] = self.video.w
                    self.videometa["HEIGHT"] = self.video.h
                    self.videometa["CHANNELS"] = 3
                    self.videometa["NFRAMES"] = self.video.nframes

                    try:
                        # Time segmentation
                        print("------------------ time seg")
                        input, out = time_segmentation(self.video)
                        self.start, self.end = extract_interest(out[0, :, 2])
                        self.videometa["FIRST_GOOD_FRAME"] = max(
                            round(self.start[0] * self.video.nframes / 500),
                            int(self.video.nframes * 0.1),
                        )
                        self.videometa["LAST_GOOD_FRAME"] = min(
                            round(self.video.nframes * self.end[-1] / 500),
                            int(self.video.nframes),
                        )
                    except:
                        self.start, self.end = 0, self.video.nframes
                        self.videometa["FIRST_GOOD_FRAME"] = self.start
                        self.videometa["LAST_GOOD_FRAME"] = self.end

                    # autoCrop
                    try:
                        print("AutoCrop: Start")
                        frame_crop_index = int(
                            self.videometa["FIRST_GOOD_FRAME"]
                            + (
                                self.videometa["FIRST_GOOD_FRAME"]
                                + self.videometa["FIRST_GOOD_FRAME"]
                            )
                            / 2
                        )
                        frame_crop = self.video.get_frame(frame_crop_index)
                        # Normalize input frame
                        frame_crop = CLAHE_normalize(frame_crop, self.clahe)
                        XMIN, XMAX, YMIN, YMAX = self.autoCrop(frame_crop)
                        self.videometa["XMIN"] = XMIN
                        self.videometa["XMAX"] = XMAX
                        self.videometa["YMIN"] = YMIN
                        self.videometa["YMAX"] = YMAX
                        print("AutoCrop: OK")
                    except:
                        self.videometa["YMIN"] = 20
                        self.videometa["YMAX"] = self.video.h
                        self.videometa["XMIN"] = int(self.video.w * 0.10)
                        self.videometa["XMAX"] = int(self.video.w * 0.90)
                    c_range = self.videometa.crop_range()
                    self.videometa.write()

                # Initialize UI
                print(
                    "************************* Last Good Frame: ",
                    self.videometa["LAST_GOOD_FRAME"],
                )
                self.ui.spinBox_FrameIndex.setRange(0, self.video.nframes - 1)
                self.ui.spinBox_FrameIndex.setValue(self.videometa["FIRST_GOOD_FRAME"])
                self.ui.spinBox_FirstGoodFrame.setValue(
                    self.videometa["FIRST_GOOD_FRAME"]
                )
                self.ui.spinBox_LastGoodFrame.setValue(
                    self.videometa["LAST_GOOD_FRAME"]
                )
                self.ui.comboBox_flowDirection.setCurrentText(
                    self.videometa["FLOW_DIRECTION"]
                )
                self.ui.lineEdit_filename.setText(self.video.name)
                self.ui.spinBox_LastGoodFrame.setRange(0, self.video.nframes - 1)
                self.ui.spinBox_FirstGoodFrame.setRange(0, self.video.nframes - 1)
                self.plot_brightness()
                self.ui.Window3.canvas.clicked.connect(self.brightness_click_slot)
                self.ui.spinBox_FirstGoodFrame.valueChanged.connect(
                    self.plot_start_stop
                )
                self.ui.spinBox_LastGoodFrame.valueChanged.connect(self.plot_start_stop)

                # load meta params
                self.frame = self.video.get_frame(self.videometa["FIRST_GOOD_FRAME"])
                c_range = self.videometa.crop_range()
                # Init processor object
                self.processor = ArcjetProcessor(
                    self.frame,
                    home=self.homedir,
                    crop_range=c_range,
                    flow_direction=self.videometa["FLOW_DIRECTION"],
                )

                # Connect UI only on first video load
                if self.VIDEO_LOADED is False:

                    self.ui.spinBox_FrameIndex.valueChanged.connect(
                        self.update_frame_index
                    )  # problem ici
                    self.frame_processed.connect(self.show_img)
                    self.ui.checkbox_display_shock.stateChanged.connect(
                        self.update_frame_index
                    )
                    self.ui.maxHue.valueChanged.connect(self.update_frame_index)
                    self.ui.minHue.valueChanged.connect(self.update_frame_index)
                    self.ui.minIntensity.valueChanged.connect(self.update_frame_index)
                    self.ui.maxIntensity.valueChanged.connect(self.update_frame_index)
                    self.ui.minSaturation.valueChanged.connect(self.update_frame_index)
                    self.ui.maxSaturation.valueChanged.connect(self.update_frame_index)

                    self.ui.maxHue_2.valueChanged.connect(self.update_frame_index)
                    self.ui.minHue_2.valueChanged.connect(self.update_frame_index)
                    self.ui.minIntensity_2.valueChanged.connect(self.update_frame_index)
                    self.ui.maxIntensity_2.valueChanged.connect(self.update_frame_index)
                    self.ui.minSaturation_2.valueChanged.connect(
                        self.update_frame_index
                    )
                    self.ui.maxSaturation_2.valueChanged.connect(
                        self.update_frame_index
                    )

                    self.ui.checkBox_crop.stateChanged.connect(self.update_frame_index)
                    if (
                        self.ui.spinBox_crop_xmin.value()
                        < self.ui.spinBox_crop_xmax.value()
                        and self.ui.spinBox_crop_ymin.value()
                        < self.ui.spinBox_crop_ymax.value()
                    ):
                        self.ui.applyCrop.clicked.connect(self.update_frame_index)

                    self.ui.comboBox_filterType.currentTextChanged.connect(
                        self.update_frame_index
                    )
                    self.ui.comboBox_flowDirection.currentTextChanged.connect(
                        self.update_frame_index
                    )
                    self.VIDEO_LOADED = True
                    ### load new image
                    self.update_frame_index()
                    self.NEW_VIDEO = False

            except Exception as e:
                print("could not load video")
                msg = QMessageBox()
                msg.setWindowTitle("ArcjetCV Warning")
                msg.setText("! Could not load video !:\n" + str(e))
                msg.setIconPixmap(QPixmap("gui/logo/arcjetCV_logo.png"))
                x = msg.exec_()

    def process_all(self):
        if not self.VIDEO_LOADED:
            return

        # Create OutputListJSON object to store results
        ilow, ihigh = (
            self.ui.spinBox_FirstGoodFrame.value(),
            self.ui.spinBox_LastGoodFrame.value(),
        )
        prefix = self.ui.lineEdit_filename.text()
        filename = "%s_%i_%i.json" % (prefix, ilow, ihigh)
        opl = OutputListJSON(os.path.join(self.video.folder, filename))

        inputdict = {"SEGMENT_METHOD": str(self.ui.comboBox_filterType.currentText())}
        inputdict["HSV_MODEL_RANGE"] = [
            (
                self.ui.minHue.value(),
                self.ui.minSaturation.value(),
                self.ui.minIntensity.value(),
            ),
            (
                self.ui.maxHue.value(),
                self.ui.maxSaturation.value(),
                self.ui.maxIntensity.value(),
            ),
        ]
        inputdict["HSV_SHOCK_RANGE"] = [
            (
                self.ui.minHue_2.value(),
                self.ui.minSaturation_2.value(),
                self.ui.minIntensity_2.value(),
            ),
            (
                self.ui.maxHue_2.value(),
                self.ui.maxSaturation_2.value(),
                self.ui.maxIntensity_2.value(),
            ),
        ]
        inputdict["THRESHOLD"] = self.ui.minIntensity.value()

        if self.VIDEO_LOADED:
            self.videometa["FIRST_GOOD_FRAME"] = ilow
            self.videometa["LAST_GOOD_FRAME"] = ihigh
            self.videometa.write()

        # processing params
        WRITEVID = self.ui.checkBox_writeVideo.isChecked()
        skips = self.ui.spinBox_frame_skips.value()

        # ------------------------------------------------------------- #
        ### Create worker thread for responsive gui during processing ###
        # ------------------------------------------------------------- #
        self.thread = WorkerThread(self.processor, self.video)

        self.thread.finished.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)

        self.thread.run(ilow, ihigh, skips, inputdict, opl, WRITEVID)

        self.raw_outputs = opl

        # Create a message box
        msg_box = QMessageBox()
        msg_box.setWindowTitle("Video Processed")
        msg_box.setText("The video has been processed.")
        msg_box.setIconPixmap(QPixmap("gui/logo/arcjetCV_logo.png"))
        msg_box.exec_()  # Display the message box

    def shorten_path(self, path, max_length):
        if len(path) <= max_length:
            return path  # Return the original path if it is already short enough

        max_visible_length = max_length - 3  # Reserve 3 characters for '...'
        first_part = path[: max_visible_length // 2]
        last_part = path[-(max_visible_length - len(first_part)) :]
        return first_part + "..." + last_part

    def load_outputs(self):
        try:
            # create fileDialog to select file
            options = QtWidgets.QFileDialog.Options()
            files, _ = QtWidgets.QFileDialog.getOpenFileNames(
                self,
                "Load ouput files",
                "",
                "Output Files (*.json);;All Files (*)",
                options=options,
            )

            self.ui.basebar.setText("Loading %i files" % len(files))

            # Load all files & concatenate
            self.raw_outputs = []
            for fname in files:
                with open(fname, "rb") as file:
                    opl = json.load(file)
                    self.raw_outputs.extend(opl)

            if len(files) > 0:
                fpath, name, ext = splitfn(files[0])
                shortpath = self.shorten_path(fpath, 30)
                # Show summary of loaded data
                summary = "Loaded %i files\n" % len(files)
                summary += "Folder: %s\n" % shortpath
                for fname in files:
                    fpath, name, ext = splitfn(fname)
                    summary += "File: %s\n" % name
                summary += "Total frames: %i\n" % len(self.raw_outputs)

                self.ui.label_data_summary.setText(summary)
                self.ui.basebar.setText("Finished loading files")
        except Exception as e:
            QMessageBox.warning(
                None, "Warning", "!!! File loading failed !!!:\n" + str(e)
            )

        self.plot_outputs()

    def init_plot_brightness(self):
        # Reset plotting windows
        self.ui.Window3.canvas.axes.clear()

        # Remove numbers on the x-axis and y-axis
        self.ui.Window3.canvas.axes.set_yticklabels([])
        self.ui.Window3.canvas.axes.get_xaxis().set_visible(False)
        self.ui.Window3.canvas.axes.get_yaxis().set_visible(False)
        self.ui.Window3.canvas.draw()

        # Hide the toolbar
        if self.ui.Window3.canvas.toolbar is not None:
            self.ui.Window3.canvas.toolbar.setVisible(False)

    def plot_location(self, reset=False):
        n = self.ui.spinBox_FrameIndex.value()
        if self._tplot_ref is None or reset:
            self._tplot_ref = self.ui.Window3.canvas.axes.axvline(
                x=n, color="red", linestyle="-"
            )

            def on_mouse_click(self, event):
                if event.button == 1:  # Left mouse button
                    x, y = event.xdata, event.ydata
                    if x is not None and y is not None:
                        self.clicked.emit(x, y)

        else:
            self._tplot_ref.set_xdata([n, n])

        self.ui.Window3.canvas.draw()

    def plot_start_stop(self):

        start = self.ui.spinBox_FirstGoodFrame.value()
        stop = self.ui.spinBox_LastGoodFrame.value()

        # Check if self.start_line exists and is not None before removing
        if self.start_line is not None:
            self.start_line.remove()
            self.start_line = None

        # Check if self.stop_line exists and is not None before removing
        if self.stop_line is not None:
            self.stop_line.remove()
            self.stop_line = None

        if 0 <= start < self.video.nframes:
            self.start_line = self.ui.Window3.canvas.axes.axvline(
                x=start, color="green", linestyle="-"
            )
        if 0 <= stop < self.video.nframes:
            self.stop_line = self.ui.Window3.canvas.axes.axvline(
                x=stop, color="green", linestyle="-"
            )
        self.ui.Window3.canvas.draw()

    def plot_brightness(self):
        # Reset plotting windows
        self.ui.Window3.canvas.axes.clear()
        self.ax1 = self.ui.Window3.canvas.axes

        brightness_signal = []
        # Calculate the brightness signal for each frame
        self.video.set_frame(0)
        for _ in range(self.video.nframes):
            ret, frame = self.video.cap.read()
            if not ret:
                break
            gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            brightness = np.mean(gray_frame)
            brightness_signal.append(brightness)

        print("### length of brightness_signal ", len(brightness_signal))
        print("### max of brightness_signal ", max(brightness_signal))
        print("### min of brightness_signal ", min(brightness_signal))
        # Plot the brightness signal
        # if self._brightness_ref is None:
        plot_refs = self.ax1.plot(brightness_signal)
        #     self._brightness_ref = plot_refs[0]
        # else:
        #     self._brightness_ref.set_ydata(brightness_signal)
        #     print(self._brightness_ref)
        self.ax1.autoscale_view()
        self.ax1.set_xlim([0, len(brightness_signal) - 1])

        # Plot the red point for the specific n value and start and stop
        self.plot_location(reset=True)
        self.plot_start_stop()
        # Remove numbers on the x-axis and y-axis
        self.ax1.set_yticklabels([])
        self.ax1.get_xaxis().set_visible(False)
        self.ax1.get_yaxis().set_visible(False)
        self.ui.Window3.canvas.draw()
        # Hide the toolbar
        if self.ui.Window3.canvas.toolbar is not None:
            self.ui.Window3.canvas.toolbar.setVisible(False)

    def plot_outputs(self):
        self.ui.basebar.setText("Setting up plots...")

        # Reset plotting windows
        self.ui.Window1.canvas.axes.clear()
        self.ui.Window2.canvas.axes.clear()

        self.ax1 = self.ui.Window1.canvas.axes
        self.ax2 = self.ui.Window2.canvas.axes

        # Plotting params
        n = len(self.raw_outputs)
        index, m75, m25, mc, p25, p75, radius = [], [], [], [], [], [], []
        time, sarea, marea, sc, sm, ypos = [], [], [], [], [], []

        diameter = self.ui.doubleSpinBox_diameter.value()
        units = self.ui.comboBox_units.currentText()
        fps = self.ui.doubleSpinBox_fps.value()
        maskn = self.ui.spinBox_mask_frames.value()

        self.ui.basebar.setText("Plotting data...")
        try:
            if len(self.raw_outputs) > 10:
                numframes = len(self.raw_outputs)
                max_traces = 10
                nskip = int(numframes / max_traces)
                for i in range(0, len(self.raw_outputs), maskn):
                    # Save frame index, time
                    index.append(self.raw_outputs[i]["INDEX"])
                    time.append(self.raw_outputs[i]["INDEX"] / fps)

                    # Model positions (-75%, -25%, center, 25%, 75% radius)
                    if self.raw_outputs[i]["MODEL"] is not None:
                        xpos = self.raw_outputs[i]["MODEL_INTERP_XPOS"]
                        center = self.raw_outputs[i]["MODEL_YCENTER"]
                        self.raw_outputs[i]["MODEL"] = np.array(
                            self.raw_outputs[i]["MODEL"]
                        )

                        m75.append(xpos[0])
                        m25.append(xpos[1])
                        mc.append(xpos[2])
                        p25.append(xpos[3])
                        p75.append(xpos[4])
                        ypos.append(center)
                        radius.append(self.raw_outputs[i]["MODEL_RADIUS"])
                    else:
                        m75.append(np.nan)
                        m25.append(np.nan)
                        mc.append(np.nan)
                        p25.append(np.nan)
                        p75.append(np.nan)
                        ypos.append(np.nan)
                        radius.append(np.nan)

                    # Shock center x-position
                    if self.raw_outputs[i]["SHOCK"] is not None:
                        sc.append(self.raw_outputs[i]["SHOCK_INTERP_XPOS"][0])
                        self.raw_outputs[i]["SHOCK"] = np.array(
                            self.raw_outputs[i]["SHOCK"]
                        )

                    else:
                        sc.append(np.nan)

                    # Shock and model area
                    if self.raw_outputs[i]["SHOCK"] is not None:
                        sarea.append(self.raw_outputs[i]["SHOCK_AREA"])
                    else:
                        sarea.append(np.nan)

                    if self.raw_outputs[i]["MODEL"] is not None:
                        marea.append(self.raw_outputs[i]["MODEL_AREA"])
                    else:
                        marea.append(np.nan)

                    # Shock-model separation, center
                    if (self.raw_outputs[i]["MODEL"] is not None) and (
                        self.raw_outputs[i]["SHOCK"] is not None
                    ):
                        sm.append(abs(sc[-1] - mc[-1]))
                    else:
                        sm.append(np.nan)

                    ### Plot XY contours
                    if nskip > 1 and i % nskip == 0:
                        if self.raw_outputs[i]["MODEL"] is not None:
                            self.ax1.plot(
                                np.array(self.raw_outputs[i]["MODEL"][:, 0, 0]),
                                np.array(self.raw_outputs[i]["MODEL"][:, 0, 1]),
                                "g-",
                                label="model_%i" % index[-1],
                            )
                        if (
                            self.raw_outputs[i]["SHOCK"] is not None
                            and self.ui.checkBox_display_shock2.isChecked()
                        ):
                            self.ax1.plot(
                                np.array(self.raw_outputs[i]["SHOCK"][:, 0, 0]),
                                np.array(self.raw_outputs[i]["SHOCK"][:, 0, 1]),
                                "r--",
                                label="shock_%i" % index[-1],
                            )
                self.ax1.set_xlabel("X (px)")
                self.ax1.set_ylabel("Y (px)")
                self.ax1.invert_yaxis()
                self.ax1.figure.canvas.draw()

                ### Mask outliers
                metrics = [marea, ypos, radius, mc]
                mask = getOutlierMask(metrics)
                self.XT_MASK = mask

                ### Infer px length
                radius_masked = np.ma.masked_where(mask < 0, radius)
                pixel_length = diameter / (2 * np.nanmax(radius_masked))
                self.pixel_length = pixel_length

                ### Plot XT series
                ym75 = np.ma.masked_where(mask < 0, m75) * pixel_length
                ym25 = np.ma.masked_where(mask < 0, m25) * pixel_length
                ymc = np.ma.masked_where(mask < 0, mc) * pixel_length
                yp25 = np.ma.masked_where(mask < 0, p25) * pixel_length
                yp75 = np.ma.masked_where(mask < 0, p75) * pixel_length
                ysarea = np.ma.masked_where(mask < 0, sarea)
                ymarea = np.ma.masked_where(mask < 0, marea)
                ysc = np.ma.masked_where(mask < 0, sc) * pixel_length
                ysm = np.ma.masked_where(mask < 0, sm) * pixel_length
                yypos = np.ma.masked_where(mask < 0, ypos) * pixel_length

                self.datasets = [
                    ym75,
                    ym25,
                    ymc,
                    yp25,
                    yp75,
                    ymarea,
                    ysarea,
                    radius_masked,
                    ymc,
                    ysc,
                    ysm,
                ]

                self.PLOTKEYS = []

                if self.ui.checkBox_m75_radius.isChecked():
                    self.ax2.plot(time, ym75, "ms", label="Model -75%R")
                    self.PLOTKEYS.append("MODEL_-0.75R " + units)

                if self.ui.checkBox_m25_radius.isChecked():
                    self.ax2.plot(time, ym25, "bx", label="Model -25%R")
                    self.PLOTKEYS.append("MODEL_-0.25R " + units)

                if self.ui.checkBox_model_center.isChecked():
                    self.ax2.plot(time, ymc, "go", label="Model center")
                    self.PLOTKEYS.append("MODEL_CENTER " + units)

                if self.ui.checkBox_25_radius.isChecked():
                    self.ax2.plot(time, yp25, "cx", label="Model +25%R")
                    self.PLOTKEYS.append("MODEL_0.25R " + units)

                if self.ui.checkBox_75_radius.isChecked():
                    self.ax2.plot(time, yp75, "rs", label="Model +75%R")
                    self.PLOTKEYS.append("MODEL_0.75R " + units)

                if self.ui.checkBox_shock_area.isChecked():
                    self.ax2.plot(time, ysarea, "y^", label="Shock area (px)")
                    self.PLOTKEYS.append("SHOCK_AREA [px]")

                if self.ui.checkBox_model_rad.isChecked():
                    self.ax2.plot(time, radius_masked, "bx", label="Model radius (px)")
                    self.PLOTKEYS.append("MODEL_RADIUS [px]")

                if self.ui.checkBox_shock_center.isChecked():
                    self.ax2.plot(time, ysc, "cs", label="Shock center")
                    self.PLOTKEYS.append("SHOCK_CENTER " + units)

                if self.ui.checkBox_shockmodel.isChecked():
                    self.ax2.plot(time, ysm, "r--", label="Shock-model distance")
                    self.PLOTKEYS.append("SHOCK_TO_MODEL " + units)

                if self.ui.checkBox_ypos.isChecked():
                    self.ax2.plot(time, yypos, "ks", label="Axis position")
                    self.PLOTKEYS.append("MODEL_YPOS " + units)

                self.ax2.set_xlabel("Time (s)")
                self.ax2.set_ylabel("%s" % (self.ui.comboBox_units.currentText()))

                legend = self.ax2.legend()
                legend.set_draggable(True)
                # self.ax2.figure.legend()
                self.ax2.figure.canvas.draw()

                # Save to dictionary data structure
                output_dict = {"TIME [s]": time}
                self.length_units = [ym75, ym25, ymc, yp25, yp75, ysc, ysm, yypos]
                self.length_labels = [
                    "MODEL_-0.75R",
                    "MODEL_-0.25R",
                    "MODEL_CENTER",
                    "MODEL_0.25R",
                    "MODEL_0.75R",
                    "SHOCK_CENTER",
                    "SHOCK_TO_MODEL",
                    "MODEL_YPOS",
                ]
                for k in range(0, len(self.length_units)):
                    output_dict[self.length_labels[k] + " " + units] = (
                        self.length_units[k]
                    )

                self.px_units = [ymarea, ysarea, radius_masked]
                self.px_labels = [
                    "MODEL_AREA [px]",
                    "SHOCK_AREA [px]",
                    "MODEL_RADIUS [px]",
                ]
                for k in range(0, len(self.px_units)):
                    output_dict[self.px_labels[k]] = self.px_units[k]

                output_dict["CONFIG"] = [
                    "UNITS: %s" % units,
                    "MODEL_DIAMETER: %.2f" % diameter,
                    "FPS: %.2f" % fps,
                    "MASK_NFRAMES: %i" % maskn,
                ]
                self.time_series = output_dict.copy()
                # self.ui.textBrowser.setText(str(self.time_series.keys()))

                # Update ui metrics
                self.ui.doubleSpinBox_fit_start_time.setMinimum(min(time))
                self.ui.doubleSpinBox_fit_start_time.setMaximum(max(time))
                self.ui.doubleSpinBox_fit_last_time.setMinimum(min(time))
                self.ui.doubleSpinBox_fit_last_time.setMaximum(max(time))

                self.ui.doubleSpinBox_fit_start_time.setValue(min(time))
                self.ui.doubleSpinBox_fit_last_time.setValue(max(time))

                # Update data summary with pixel length
                summary = self.ui.label_data_summary.text()
                lines = summary.strip().split("\n")
                if lines[-1][0:5] == "Pixel":
                    lines[-1] = "Pixel length %s: %.4f" % (
                        self.ui.comboBox_units.currentText(),
                        pixel_length,
                    )
                else:
                    lines.append(
                        "Pixel length %s: %.4f"
                        % (self.ui.comboBox_units.currentText(), pixel_length)
                    )
                newsummary = ""
                for line in lines:
                    newsummary += line + "\n"
                self.ui.label_data_summary.setText(newsummary.strip())

                # Infobar update
                self.ui.basebar.setText("Finished plotting data")
            else:
                # Infobar update
                self.ui.basebar.setText("Not enough data to plot")
                QMessageBox.warning(
                    None,
                    "Warning",
                    "!!! Not enough data to plot !!!: only %i points"
                    % len(self.raw_outputs),
                )

        except Exception as e:
            self.ui.basebar.setText("!!! Plotting failed !!!")
            QMessageBox.warning(None, "Warning", "!!! Plotting failed !!!:\n" + str(e))

        # self.ui.Window1.update()
        self.ui.Window1.repaint()
        # self.ui.Window2.update()
        self.ui.Window2.repaint()

        self.fit_data()

    def save_plots(self, name):
        try:
            # Extract necessary data from self.time_series
            time = self.time_series["TIME [s]"]
            units = self.ui.comboBox_units.currentText()

            # Plot each dataset in a separate graph
            for data, label in zip(self.length_units[5:], self.length_labels[5:]):
                fig, ax = plt.subplots()
                ax.scatter(time, data, label=label)
                ax.set_xlabel("Time (s)")
                ax.set_ylabel(f"{label} ({units})")
                ax.legend()
                filename = f"_{label.replace(' ', '_').lower()}.png"
                fig.savefig(str(name + filename))
                plt.close(fig)

                # Plot each dataset in a separate graph
            for data, label in zip(self.px_units, self.px_labels):
                fig, ax = plt.subplots()
                ax.scatter(time, data, label=label)
                ax.set_xlabel("Time (s)")
                ax.set_ylabel(f"{label} ({units})")
                ax.legend()
                filename = f"_{label.replace(' ', '_').lower()}.png"
                fig.savefig(str(name + filename))
                plt.close(fig)

            # Plot "MODEL_-0.75R", "MODEL_-0.25R", "MODEL_CENTER", "MODEL_0.25R", "MODEL_0.75R" in one graph
            fig, ax_combined = plt.subplots()
            for i, data in enumerate(self.length_units[:5]):
                label = f"Model {['-0.75R', '-0.25R', 'Center', '0.25R', '0.75'][i]}"
                ax_combined.scatter(time, data, label=label)
            ax_combined.set_xlabel("Time (s)")
            ax_combined.set_ylabel(f"Model Positions ({units})")
            ax_combined.legend()
            fig.savefig(name + "_radius.png")
            plt.close(fig)

        except Exception as e:
            self.ui.basebar.setText("!!! Plot saving failed !!!")
            QMessageBox.warning(
                None, "Warning", "!!! Plot saving failed !!!:\n" + str(e)
            )

    def export_to_csv(self):
        if self.time_series is not None:
            try:
                dialog = QtWidgets.QFileDialog()
                pathmask = dialog.getExistingDirectory(None, "Export CSV/plots", "")
                os.makedirs(pathmask, exist_ok=True)
                folder_path = os.path.abspath(pathmask)
                folder_name = os.path.basename(pathmask)

                self.ax1.figure.savefig(
                    os.path.join(folder_path, folder_name + "_xy.png")
                )
                self.ax2.figure.savefig(
                    os.path.join(folder_path, folder_name + "_xt.png")
                )
                self.save_plots(os.path.join(folder_path, folder_name))

                ### Convert time series into dataframe
                df = pd.DataFrame(
                    dict([(k, pd.Series(v)) for k, v in self.time_series.items()])
                )

                ### Convert fits into dataframe
                if self.fit_dict is not None:
                    param_dict = {"Pixel length": self.pixel_length}
                    # Create pandas Series from fitparam dictionary
                    keys, vals, errs = [], [], []
                    for key, val in self.fit_dict.items():
                        if "LINEAR_FIT" in key:
                            keys.append(key + "_slope")
                            keys.append(key + "_intercept")
                            vals.append(val[0][0])
                            vals.append(val[0][1])
                            errs.append(val[1][0])
                            errs.append(val[1][1])

                    # Create pandas Series from fitparam dictionary
                    keys_series = pd.Series(keys)
                    values_series = pd.Series(vals)
                    err_series = pd.Series(errs)
                    param_dict.update(self.fit_dict)

                    # Assign the Series as new columns to the DataFrame
                    df = df.assign(
                        Keys=keys_series, Values=values_series, Error=err_series
                    )

                    csv_file_path = os.path.join(folder_path, f"{folder_name}.csv")
                    df.to_csv(csv_file_path, index=False)

            except Exception as e:
                self.ui.basebar.setText("!!! CSV export failed !!!")
                QMessageBox.warning(
                    None, "Warning", "!!! CSV export failed !!!:\n" + str(e)
                )

    def fit_data(self):
        if self.time_series is not None:

            try:
                ### Retrieve user inputs for time/units
                units = self.ui.comboBox_units.currentText()
                time = np.array(self.time_series["TIME [s]"])
                mask = np.array(self.XT_MASK)
                t0 = self.ui.doubleSpinBox_fit_start_time.value()
                t1 = self.ui.doubleSpinBox_fit_last_time.value()

                ### identify relevant indicies
                inds = (time > t0) * (time < t1) * (mask > 0)

                ### Initialize data structure
                fit_dict = {}

                ### Get list of keys to loop through
                keys = list(self.time_series.keys())
                keys.remove("TIME [s]")
                keys.remove("CONFIG")

                ### Linear fits
                if self.ui.comboBox_fit_type.currentText() == "linear":
                    longstring = ""
                    for key in keys:
                        t = time[inds]
                        y = self.time_series[key][inds]
                        if len(t) > 2 and len(y) > 2:
                            fitp, cov = np.ma.polyfit(t, y, 1, cov=True)
                            err = np.sqrt(np.diag(cov))
                            m, b = fitp[0], fitp[1]
                            fit_dict[key + "_LINEAR_FIT"] = (fitp, err)
                            if key in self.PLOTKEYS:
                                longstring += (
                                    key
                                    + "\tMin = %f\t Max = %f\t Delta = %f\n"
                                    % (y.min(), y.max(), y.max() - y.min())
                                )
                                longstring += "\tLINEAR FIT: y = mx+b \t"
                                longstring += (
                                    "m = %f+-%f %s" % (m, err[0], units + "/s") + "\t"
                                )
                                longstring += (
                                    "b = %f+-%f %s" % (b, err[1], units) + "\n\n"
                                )
                        else:
                            longstring = "not enough points to fit data"

                    self.ui.textBrowser.setText(longstring)
                    self.ui.textBrowser.repaint()

                ### Quadratic fits
                if self.ui.comboBox_fit_type.currentText() == "quadratic":
                    longstring = ""
                    for key in keys:
                        t = time[inds]
                        y = self.time_series[key][inds]
                        if t and y:
                            fitp, cov = np.polyfit(t, y, 2, cov=True)
                            err = np.sqrt(np.diag(cov))
                            a, b, c = fitp[0], fitp[1], fitp[2]
                            fit_dict[key + "_QUADRATIC_FIT"] = (fitp, err)
                            if key in self.PLOTKEYS:
                                longstring += (
                                    key
                                    + "\tMin = %f\t Max = %f\t Delta = %f\n"
                                    % (y.min(), y.max(), y.max() - y.min())
                                )
                                longstring += "\tQUAD FIT: y = a*t^2 + b*t + c \n"
                                longstring += (
                                    "a = %f+-%f %s" % (a, err[0], units + "/s^2") + "\t"
                                )
                                longstring += (
                                    "b = %f+-%f %s" % (b, err[1], units + "/s") + "\t"
                                )
                                longstring += (
                                    "c = %f+-%f %s" % (c, err[2], units) + "\n\n"
                                )
                            else:
                                longstring = "not enough points to fit data"
                    self.ui.textBrowser.setText(longstring)
                    self.ui.textBrowser.repaint()

                self.fit_dict = fit_dict

            except Exception as e:
                self.ui.basebar.setText("!!! Fitting failed !!!")
                QMessageBox.warning(
                    None, "Warning", "!!! Fitting failed !!!:\n" + str(e)
                )


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
