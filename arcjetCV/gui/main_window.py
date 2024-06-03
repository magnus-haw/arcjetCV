import os
from pathlib import Path
import numpy as np
import pandas as pd
import cv2 as cv
import json
from numbers import Number
from PySide6 import QtWidgets
from PySide6.QtWidgets import QMessageBox
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon,QPixmap
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv
from matplotlib.widgets import RectangleSelector
from arcjetCV.gui.arcjetCV_gui import Ui_MainWindow
from arcjetCV.utils.video import Video, VideoMeta
from arcjetCV.utils.processor import ArcjetProcessor
from arcjetCV.utils.utils import (
    splitfn,
    getOutlierMask,
    annotateImage,
    annotate_image_with_frame_number,
)


class MainWindow(QtWidgets.QMainWindow):
    frame_processed = Signal()

    def __init__(self):
        super().__init__()

        # Initialize the user interface
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.testing = False

        # Set the application icon
        self.logo_white_path = os.path.join(
            Path(__file__).parent.absolute(), "logo/arcjetCV_logo_white.png"
        )
        self.logo_path = os.path.join(Path(__file__).parent.absolute(), "logo/arcjetCV_logo_.png")
        self.setWindowIcon(QIcon(self.logo_path))

        # Load and process the application logo
        self.rgb_frame = cv.imread(self.logo_white_path)
        self.rgb_frame = cv.cvtColor(self.rgb_frame, cv.COLOR_BGR2RGB)

        # Initialize frame and plotting windows
        self._plot_ref = None
        self._tplot_ref = None
        self._brightness_ref = None
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
        self.ui.checkBox_m95_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_m50_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_model_center.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_50_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_95_radius.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_shock_area.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_model_rad.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_shock_center.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_shockmodel.stateChanged.connect(self.plot_outputs)
        self.ui.checkBox_ypos.stateChanged.connect(self.plot_outputs)
        self.ui.applyCrop.clicked.connect(self.update_crop)
        self.ui.comboBox_units.setCurrentText("[mm]")

        # init_plot_brightness
        self.ui.Window3.canvas.axes.clear()
        self.ui.Window3.canvas.axes.set_yticklabels([])
        self.ui.Window3.canvas.axes.get_xaxis().set_visible(False)
        self.ui.Window3.canvas.axes.get_yaxis().set_visible(False)
        if self.ui.Window3.canvas.toolbar is not None:
            self.ui.Window3.canvas.toolbar.setVisible(False)
        self.ui.Window3.canvas.draw()

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
        if self._plot_ref is None:
            # Create a new plot reference and define the cursor data format
            self._plot_ref = self.ui.label_img.canvas.axes.imshow(
                self.rgb_frame, aspect="equal"
            )
            self._plot_ref.axes.get_xaxis().set_visible(False)
            self._plot_ref.axes.get_yaxis().set_visible(False)

            # Customize axis spines color to match the background (hiding the border)
            self._plot_ref.axes.spines["top"].set_color("none")
            self._plot_ref.axes.spines["bottom"].set_color("none")
            self._plot_ref.axes.spines["left"].set_color("none")
            self._plot_ref.axes.spines["right"].set_color("none")

            def format_cursor_data(data):
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

            self._plot_ref.format_cursor_data = format_cursor_data
            self.rect_selector = RectangleSelector(self._plot_ref.axes, self.onselect)
        else:
            self._plot_ref.set_data(self.rgb_frame)

        self.ui.label_img.canvas.draw()

    def onselect(self, eclick, erelease):
        x1, y1 = eclick.xdata, eclick.ydata
        x2, y2 = erelease.xdata, erelease.ydata
        self.ui.spinBox_crop_xmin.setValue(x1)
        self.ui.spinBox_crop_xmax.setValue(x2)
        self.ui.spinBox_crop_ymin.setValue(y1)
        self.ui.spinBox_crop_ymax.setValue(y2)
        self.update_crop()

    def update_crop(self):
        # Validate bounding box inputs here
        if (
            self.ui.spinBox_crop_xmax.value() - self.ui.spinBox_crop_xmin.value() >= 40
            and self.ui.spinBox_crop_ymax.value() - self.ui.spinBox_crop_ymin.value()
            >= 40
        ):
            self.videometa["CROP_XMIN"] = self.ui.spinBox_crop_xmin.value()
            self.videometa["CROP_XMAX"] = self.ui.spinBox_crop_xmax.value()
            self.videometa["CROP_YMIN"] = self.ui.spinBox_crop_ymin.value()
            self.videometa["CROP_YMAX"] = self.ui.spinBox_crop_ymax.value()
            self.videometa.write()
            self.update_frame_index()
        else:
            pass

    def brightness_click_slot(self, x, y):
        try:
            if x > 0 and x < self.video.nframes - 1:
                self.ui.spinBox_FrameIndex.setValue(int(x))
        except:
            pass

    def update_frame_index(self):

        if self.NEW_VIDEO:
            self.ui.spinBox_crop_xmin.setValue(self.videometa["CROP_XMIN"])
            self.ui.spinBox_crop_xmax.setValue(self.videometa["CROP_XMAX"])
            self.ui.spinBox_crop_ymin.setValue(self.videometa["CROP_YMIN"])
            self.ui.spinBox_crop_ymax.setValue(self.videometa["CROP_YMAX"])

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

        # disabled the tabs with CNN
        if (
            self.ui.comboBox_filterType.currentText() == "CNN"
            or self.ui.comboBox_filterType.currentText() == "AutoHSV"
        ):
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
        self.rgb_frame = self.video.get_frame(frame_index)
        if self.rgb_frame is None:
            return

        self.processor.flow_dir = self.ui.comboBox_flowDirection.currentText()

        crop_range = [
            [self.ui.spinBox_crop_ymin.value(), self.ui.spinBox_crop_ymax.value()],
            [self.ui.spinBox_crop_xmin.value(), self.ui.spinBox_crop_xmax.value()],
        ]

        # Apply crop params
        if self.processor.crop != crop_range:
            self.processor.crop = crop_range
            if (
                self.VIDEO_LOADED
            ):  # To avoid crash (can be applied to all the function update_frame)
                self.videometa["CROP_YMIN"] = self.ui.spinBox_crop_ymin.value()
                self.videometa["CROP_XMIN"] = self.ui.spinBox_crop_xmin.value()
                self.videometa["CROP_YMAX"] = self.ui.spinBox_crop_ymax.value()
                self.videometa["CROP_XMAX"] = self.ui.spinBox_crop_xmax.value()
                self.videometa.write()

        # Process frame
        contour_dict, argdict = self.processor.process(
            self.rgb_frame, self.grab_ui_values()
        )

        # Draw contours
        for key in contour_dict.keys():
            if key == "MODEL":
                cv.drawContours(self.rgb_frame, contour_dict[key], -1, (0, 255, 0), 2)
            elif key == "SHOCK" and self.ui.checkBox_display_shock.isChecked():
                cv.drawContours(self.rgb_frame, contour_dict[key], -1, (255, 0, 0), 2)

        # Draw annotations
        annotate_image_with_frame_number(self.rgb_frame, frame_index)
        if self.ui.checkBox_annotate.isChecked():
            annotateImage(self.rgb_frame, argdict, top=True, left=True)

        # Draw Crop box
        if self.ui.checkBox_crop.isChecked():
            start_point = (self.processor.crop[1][0], self.processor.crop[0][0])
            end_point = (self.processor.crop[1][1], self.processor.crop[0][1])
            cv.rectangle(self.rgb_frame, start_point, end_point, (255, 255, 255), 2)

        self.frame_processed.emit()
        self.plot_location()

    def connect_elements(self):
        self.ui.spinBox_FrameIndex.valueChanged.connect(self.update_frame_index)
        self.frame_processed.connect(self.show_img)
        self.ui.checkBox_display_shock.stateChanged.connect(self.update_frame_index)
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
        self.ui.minSaturation_2.valueChanged.connect(self.update_frame_index)
        self.ui.maxSaturation_2.valueChanged.connect(self.update_frame_index)
        self.ui.checkBox_crop.stateChanged.connect(self.update_frame_index)
        if (
            self.ui.spinBox_crop_xmin.value() < self.ui.spinBox_crop_xmax.value()
            and self.ui.spinBox_crop_ymin.value() < self.ui.spinBox_crop_ymax.value()
        ):
            self.ui.applyCrop.clicked.connect(self.update_frame_index)
        self.ui.comboBox_filterType.currentTextChanged.connect(self.update_frame_index)
        self.ui.comboBox_flowDirection.currentTextChanged.connect(
            self.update_frame_index
        )

    def load_video(self):
        print("------New Video-----")
        dialog = QtWidgets.QFileDialog()
        options = QtWidgets.QFileDialog.Options()
        pathmask = dialog.getOpenFileName(
            None,
            "Select Video",
            "",
            "Video Files (*.mp4 *.avi *.mov *.m4v);;All Files (*)",
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

            try:  # Create video object
                self.video = Video(self.path)
                self.videometa = VideoMeta(
                    self.video, os.path.join(self.folder, self.filename + ".meta")
                )
                print("Number of Frames: ", self.video.nframes)
                print(
                    f"First-Last Good Frame: {self.videometa['FIRST_GOOD_FRAME']}-{self.videometa['LAST_GOOD_FRAME']}"
                )
                print(
                    f"Min-Max Brightness: {min(self.videometa['BRIGHTNESS'])}-{max(self.videometa['BRIGHTNESS'])}"
                )

                # Initialize UI
                self.ui.Window3.canvas.axes.clear()
                self.ax1 = self.ui.Window3.canvas.axes
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

                # Plot the brightness signal
                self.ax1.plot(self.videometa["BRIGHTNESS"])
                self.ax1.autoscale_view()
                self.ax1.set_xlim([0, self.video.nframes - 1])

                # Plot the red point for the specific n value and start and stop
                self.plot_location(reset=True)
                self.plot_start_stop()

                self.ui.Window3.canvas.draw()

                self.ui.Window3.canvas.clicked.connect(self.brightness_click_slot)
                self.ui.spinBox_FirstGoodFrame.valueChanged.connect(
                    self.plot_start_stop
                )
                self.ui.spinBox_LastGoodFrame.valueChanged.connect(self.plot_start_stop)

                if self.processor is None:
                    self.processor = ArcjetProcessor(self.videometa)
                else:  # avoid reimporting CNN model each time
                    self.processor.update_video_meta(self.videometa)

                # Connect UI only on first video load
                if self.VIDEO_LOADED is False:
                    self.connect_elements()
                    self.VIDEO_LOADED = True

                    self.update_frame_index()
                    self.NEW_VIDEO = False

            except Exception as e:
                if self.testing:
                    print("! Could not load video !:\n" + str(e))
                else:
                    msg = QMessageBox()
                    msg.setWindowTitle("arcjetCV Warning")
                    msg.setText("! Could not load video !:\n" + str(e))
                    msg.setIcon(QMessageBox.Critical)
                    msg.exec()

    def plot_location(self, reset=False):
        n = self.ui.spinBox_FrameIndex.value()
        if self._tplot_ref is None or reset:
            self._tplot_ref = self.ui.Window3.canvas.axes.axvline(
                x=n, color="red", linestyle="-"
            )
        else:
            self._tplot_ref.set_xdata([n, n])
        self.ui.Window3.canvas.draw()

    def plot_start_stop(self):
        start = self.ui.spinBox_FirstGoodFrame.value()
        stop = self.ui.spinBox_LastGoodFrame.value()

        if self.start_line is not None:
            self.start_line.remove()
            self.start_line = None
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

    def process_all(self):
        if not self.VIDEO_LOADED:
            return

        # Create OutputListJSON object to store results
        ilow, ihigh = (
            self.ui.spinBox_FirstGoodFrame.value(),
            self.ui.spinBox_LastGoodFrame.value(),
        )

        self.videometa["FIRST_GOOD_FRAME"] = ilow
        self.videometa["LAST_GOOD_FRAME"] = ihigh
        self.videometa.write()

        # Process all frames
        self.processor.process_all(
            self.video,
            self.grab_ui_values(),
            ilow,
            ihigh,
            self.ui.spinBox_frame_skips.value(),
            output_prefix=self.ui.lineEdit_filename.text(),
            write_json=True,
            write_video=self.ui.checkBox_writeVideo.isChecked(),
            display_shock=self.ui.checkBox_display_shock.isChecked(),
        )

        # Create a message box
        if self.testing:
            print("The video has been processed.")
        else:
            self.msg_box = QMessageBox()
            self.msg_box.setWindowTitle("Video Processed")
            self.msg_box.setText("The video has been processed.")
            self.msg_box.setIcon(QMessageBox.Information)
            self.msg_box.exec()  # Display the message box
        return True

    def grab_ui_values(self):
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
        return inputdict

    # PLOTTING DATA TAB
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
            if self.testing:
                print("! File loading failed !:\n" + str(e))
            else:
                self.arcjetcv_message_box("Warning", "! File loading failed !:\n" + str(e)
                )

        self.plot_outputs()

    @staticmethod
    def shorten_path(path, max_length):
        if len(path) <= max_length:
            return path  # Return the original path if it is already short enough

        max_visible_length = max_length - 3  # Reserve 3 characters for '...'
        first_part = path[: max_visible_length // 2]
        last_part = path[-(max_visible_length - len(first_part)) :]
        return first_part + "..." + last_part

    def plot_outputs(self):
        self.ui.basebar.setText("Setting up plots...")

        # Reset plotting windows
        self.ui.Window1.canvas.axes.clear()
        self.ui.Window2.canvas.axes.clear()

        self.ax1 = self.ui.Window1.canvas.axes
        self.ax2 = self.ui.Window2.canvas.axes

        # Plotting params
        index, m95, m50, mc, p50, p95, radius = [], [], [], [], [], [], []
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

                    # Model positions (-95%, -50%, center, 50%, 95% radius)
                    if self.raw_outputs[i]["MODEL"] is not None:
                        xpos = self.raw_outputs[i]["MODEL_INTERP_XPOS"]
                        center = self.raw_outputs[i]["MODEL_YCENTER"]
                        self.raw_outputs[i]["MODEL"] = np.array(
                            self.raw_outputs[i]["MODEL"]
                        )
                        m95.append(xpos[0])
                        m50.append(xpos[1])
                        mc.append(xpos[2])
                        p50.append(xpos[3])
                        p95.append(xpos[4])
                        ypos.append(center)
                        radius.append(self.raw_outputs[i]["MODEL_RADIUS"])
                    else:
                        m95.append(np.nan)
                        m50.append(np.nan)
                        mc.append(np.nan)
                        p50.append(np.nan)
                        p95.append(np.nan)
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
                    if (
                        self.raw_outputs[i]["MODEL"] is not None
                        and self.raw_outputs[i]["SHOCK"] is not None
                    ):
                        sm.append(abs(sc[-1] - mc[-1]))
                    else:
                        sm.append(np.nan)

                    # Plot XY contours
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

                # Mask outliers
                metrics = [marea, ypos, radius, mc]
                mask = getOutlierMask(metrics)
                self.XT_MASK = mask

                # Infer px length
                radius_masked = np.ma.masked_where(mask < 0, radius)
                pixel_length = diameter / (2 * np.nanmax(radius_masked))
                self.pixel_length = pixel_length

                # Plot XT series
                ym95 = np.ma.masked_where(mask < 0, m95) * pixel_length
                ym50 = np.ma.masked_where(mask < 0, m50) * pixel_length
                ymc = np.ma.masked_where(mask < 0, mc) * pixel_length
                yp50 = np.ma.masked_where(mask < 0, p50) * pixel_length
                yp95 = np.ma.masked_where(mask < 0, p95) * pixel_length
                ysarea = np.ma.masked_where(mask < 0, sarea)
                ymarea = np.ma.masked_where(mask < 0, marea)
                ysc = np.ma.masked_where(mask < 0, sc) * pixel_length
                ysm = np.ma.masked_where(mask < 0, sm) * pixel_length
                yypos = np.ma.masked_where(mask < 0, ypos) * pixel_length

                self.PLOTKEYS = []

                if self.ui.checkBox_m95_radius.isChecked():
                    self.ax2.plot(time, ym95, "ms", label="Model -95%R")
                    self.PLOTKEYS.append("MODEL_-0.95R " + units)

                if self.ui.checkBox_m50_radius.isChecked():
                    self.ax2.plot(time, ym50, "bx", label="Model -50%R")
                    self.PLOTKEYS.append("MODEL_-0.50R " + units)

                if self.ui.checkBox_model_center.isChecked():
                    self.ax2.plot(time, ymc, "go", label="Model center")
                    self.PLOTKEYS.append("MODEL_CENTER " + units)

                if self.ui.checkBox_50_radius.isChecked():
                    self.ax2.plot(time, yp50, "cx", label="Model +50%R")
                    self.PLOTKEYS.append("MODEL_0.50R " + units)

                if self.ui.checkBox_95_radius.isChecked():
                    self.ax2.plot(time, yp95, "rs", label="Model +95%R")
                    self.PLOTKEYS.append("MODEL_0.95R " + units)

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
                self.ax2.figure.canvas.draw()

                # Save to dictionary data structure
                output_dict = {"TIME [s]": time}
                self.length_units = [ym95, ym50, ymc, yp50, yp95, ysc, ysm, yypos]
                self.length_labels = [
                    "MODEL_-0.95R",
                    "MODEL_-0.50R",
                    "MODEL_CENTER",
                    "MODEL_0.50R",
                    "MODEL_0.95R",
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
                self.ui.basebar.setText("Finished plotting data")
            else:
                self.ui.basebar.setText("Not enough data to plot")
                if self.testing:
                    print("Not enough data to plot")
                else:
                    self.arcjetcv_message_box(
                        "Warning",
                        "! Not enough data to plot !: only %i points"
                        % len(self.raw_outputs)
                    )

        except Exception as e:
            self.ui.basebar.setText("! Plotting failed !")
            if self.testing:
                print("Warning", "! Plotting failed !:\n" + str(e))
            else:
                self.arcjetcv_message_box("Warning", "! Plotting failed !:\n" + str(e)
                )

        self.ui.Window1.repaint()
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

            # Plot "MODEL_-0.95R", "MODEL_-0.50R", "MODEL_CENTER", "MODEL_0.50R", "MODEL_0.95R" in one graph
            fig, ax_combined = plt.subplots()
            for i, data in enumerate(self.length_units[:5]):
                label = f"Model {['-0.95R', '-0.50R', 'Center', '0.50R', '0.95'][i]}"
                ax_combined.scatter(time, data, label=label)
            ax_combined.set_xlabel("Time (s)")
            ax_combined.set_ylabel(f"Model Positions ({units})")
            ax_combined.legend()
            fig.savefig(name + "_radius.png")
            plt.close(fig)

        except Exception as e:
            self.ui.basebar.setText("! Plot saving failed !")
            if self.testing:
                print("Warning", "! Plot saving failed !:\n" + str(e))
            else:
                self.arcjetcv_message_box("Warning", "! Plot saving failed !:\n" + str(e)
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

                # Convert time series into dataframe
                df = pd.DataFrame(
                    dict([(k, pd.Series(v)) for k, v in self.time_series.items()])
                )

                # Convert fits into dataframe
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
                self.ui.basebar.setText("! CSV export failed !")
                if self.testing:
                    print("Warning", "! CSV export failed !:\n" + str(e))
                else:
                    self.arcjetcv_message_box("Warning", "! CSV export failed !:\n" + str(e)
                    )

    def fit_data(self):
        if self.time_series is not None:

            try:
                # Retrieve user inputs for time/units
                units = self.ui.comboBox_units.currentText()
                time = np.array(self.time_series["TIME [s]"])
                mask = np.array(self.XT_MASK)
                t0 = self.ui.doubleSpinBox_fit_start_time.value()
                t1 = self.ui.doubleSpinBox_fit_last_time.value()

                # identify relevant indicies
                inds = (time > t0) * (time < t1) * (mask > 0)

                # Initialize data structure
                fit_dict = {}

                # Get list of keys to loop through
                keys = list(self.time_series.keys())
                keys.remove("TIME [s]")
                keys.remove("CONFIG")

                # Linear fits
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

                self.fit_dict = fit_dict

            except Exception as e:
                self.ui.basebar.setText("! Fitting failed !")
                if self.testing:
                    print("Warning", "! Fitting failed !:\n" + str(e))
                else:
                    self.arcjetcv_message_box("Warning", "! Fitting failed !:\n" + str(e))

    def arcjetcv_message_box(self,title,message):

        msg_box = QMessageBox()
        msg_box.setIconPixmap(QPixmap(self.logo_path))
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.exec_()
