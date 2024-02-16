import sys
import cv2 as cv
import numpy as np
from pathlib import Path

from PySide6 import QtCore, QtWidgets
from PySide6.QtWidgets import QPushButton, QFileDialog, QTextEdit, QSpinBox, QMessageBox
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar,
)
from matplotlib.figure import Figure
from matplotlib.widgets import RectangleSelector, PolygonSelector
from matplotlib.backend_bases import key_press_handler
from matplotlib.path import Path as Polypath
from matplotlib.colors import ListedColormap

# Add the project root to the system path
current_directory = Path(__file__).resolve().parent
project_root = current_directory.parent  # Navigate to the project root
sys.path.append(str(project_root))

from utils.Functions import CLAHE_normalize, splitfn, convert_mask_gray_to_BGR


class CustomToolbar(NavigationToolbar):
    def __init__(self, *args, **kwargs):
        super(CustomToolbar, self).__init__(*args, **kwargs)
        self.remove_unwanted_buttons()
        self.add_draw_button()
        self.add_roi_button()
        self.add_mask_button()

    def remove_unwanted_buttons(self):
        unwanted_tooltips = [
            "Back",
            "Forward",
            "Configure subplots",
            "Edit axis, curve and image parameters",
        ]

        for action in self.actions():
            if any(tooltip in action.toolTip() for tooltip in unwanted_tooltips):
                self.removeAction(action)

    def add_draw_button(self):
        self.draw_action = QAction("Draw", self)
        self.draw_action.setCheckable(True)
        self.addAction(self.draw_action)

    def add_roi_button(self):
        self.roi_action = QAction("ROI", self)
        self.roi_action.setCheckable(True)
        self.addAction(self.roi_action)

    def add_mask_button(self):
        self.mask_action = QAction("Mask", self)
        self.mask_action.setCheckable(True)
        self.addAction(self.mask_action)


class MplCanvas(FigureCanvas):
    clicked = QtCore.Signal(float, float)

    def __init__(self, parent=None, width=5, height=4, dpi=100, master_axes=None):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.figure.set_tight_layout(True)
        self.axes = self.figure.add_subplot(121)
        self.ax2 = self.figure.add_subplot(122, sharex=self.axes, sharey=self.axes)
        self.ax2.set_aspect("equal")
        self.axes.set_aspect("equal")
        super(MplCanvas, self).__init__(self.figure)


class SegmentationWidget(QtWidgets.QWidget):
    def __init__(self, roi_checkbox=None, draw_checkbox=None, main_window=None, *args):
        super().__init__(*args)
        layout = QtWidgets.QVBoxLayout(self)
        self.canvas = MplCanvas(self)
        self.canvas.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.canvas.setFocus()
        self.toolbar = CustomToolbar(self.canvas, self)
        self.main_window = main_window

        self.drawing_case = 1
        self.roi_mode = False
        self.draw_mode = False
        self.mask_mode = True
        self.maskplot_ref = None
        self.imageplot_ref = None

        # Grabcut variables
        self.bgdmodel = np.zeros((1, 65), np.float64)
        self.fgdmodel = np.zeros((1, 65), np.float64)
        self.rect = (0, 0, 1, 1)
        self.colors = ["red", "green", "blue", "cyan"]
        self.mask_cmap = ListedColormap(self.colors)  # Define the custom colormap

        # External controls
        self.roi_checkbox = roi_checkbox
        self.draw_checkbox = draw_checkbox

        # Connect signals to actions
        self.toolbar.draw_action.toggled.connect(self.toggle_draw_mode)
        self.toolbar.roi_action.toggled.connect(self.toggle_roi_mode)
        self.toolbar.mask_action.toggled.connect(self.toggle_mask_mode)
        self.canvas.mpl_connect("key_press_event", self.on_key_press)
        # self.main_window.frame_spinbox.valueChanged.connect(self.main_window.update_video_frame)

        # Create a rectangle selector for ROI
        self.rs = RectangleSelector(
            self.canvas.axes,
            self.roi_select_callback,
            useblit=True,
            button=[1],
            minspanx=5,
            minspany=5,
            spancoords="pixels",
            interactive=True,
            props=dict(facecolor="none", edgecolor="green", linewidth=1.5),
        )
        self.rs.set_active(False)

        # Create a polygon selector for annotations
        line_properties = {"color": "blue", "linewidth": 2}
        vertex_properties = {
            "color": "red",
            "markersize": 3,
        }  # 'size' controls the size of the dots

        self.ps = PolygonSelector(
            self.canvas.axes,
            self.polygon_select_callback,
            useblit=True,
            props=line_properties,
            handle_props=vertex_properties,
        )
        self.ps.set_active(False)

        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_mask(self):
        image = convert_mask_gray_to_BGR(self.main_window.mask)
        if self.maskplot_ref is None:
            self.maskplot_ref = self.canvas.ax2.imshow(image, origin="upper")
        else:
            self.maskplot_ref.set_data(image)

    def reset_all(self):
        self.main_window.mask = np.zeros_like(self.main_window.mask, dtype=np.uint8)
        self.bgdmodel = np.zeros((1, 65), np.float64)
        self.fgdmodel = np.zeros((1, 65), np.float64)
        try:
            self.maskplot_ref.remove()
        except:
            pass
        self.maskplot_ref = None
        self.rect = (0, 0, 1, 1)
        self.update_mask()
        self.main_window.add_log_entry("Reset mask and annotations")
        self.canvas.draw()

    def on_key_press(self, event):
        """
        Key '0' - To select areas of sure background
        Key '1' - To select areas of sure foreground
        Key '2' - To select areas of probable background
        Key '3' - To select areas of probable foreground

        Key 'n' - To update the segmentation
        Key 'r' - To reset the ROI
        Key 's' - To save the results
        Key 'c' - To clear the mask & ROI
        Key 'm' - To toggle the masked image
        """
        print("press", event.key)
        if event.key == "d":  # draw mode
            self.toggle_draw_mode()
        elif event.key == "r":  # roi mode
            self.toggle_roi_mode()
        elif event.key == "0":  # annotation types
            self.drawing_case = int(event.key)
            self.main_window.add_log_entry("Annotating: Sure Background")
        elif event.key == "1":  # annotation types
            self.drawing_case = int(event.key)
            self.main_window.add_log_entry("Annotating: Sure Foreground")
        elif event.key == "2":  # annotation types
            self.drawing_case = int(event.key)
            self.main_window.add_log_entry("Annotating: Probably Background")
        elif event.key == "3":  # annotation types
            self.drawing_case = int(event.key)
            self.main_window.add_log_entry("Annotating: Probable Foreground")
        elif event.key == "c":
            self.reset_all()
        elif event.key == "u":
            self.update_mask()
        elif event.key == "m":
            self.toggle_mask_mode()
        elif event.key == "n":
            try:
                if (
                    self.main_window.mask.sum() == 0
                ):  # initialize first grabcut with rect
                    initparam = cv.GC_INIT_WITH_RECT
                else:
                    initparam = cv.GC_INIT_WITH_MASK

                ret = cv.grabCut(
                    self.main_window.image,
                    self.main_window.mask,
                    self.rect,
                    self.bgdmodel,
                    self.fgdmodel,
                    1,
                    initparam,
                )
                self.main_window.mask, self.fgdmodel, self.bgdmodel = ret
            except:
                import traceback

                traceback.print_exc()
            self.update_mask()
            self.canvas.draw()
        else:
            key_press_handler(event, self.canvas, self.toolbar)

    def toggle_roi_mode(self):
        if not self.main_window.image_loaded:
            return
        self.roi_mode = not self.roi_mode
        if self.roi_mode and self.toolbar.mode == "pan/zoom":
            # If the pan tool is active, deactivate it
            self.toolbar.pan()
        if self.roi_mode and self.toolbar.mode == "zoom rect":
            # If the zoom tool is active, deactivate it
            self.toolbar.zoom()
        if self.roi_mode and self.draw_mode:
            self.toggle_draw_mode()
        self.main_window.add_log_entry("ROI mode: %s" % str(self.roi_mode))
        if self.roi_checkbox is not None:
            self.roi_checkbox.setChecked(self.roi_mode)
        self.rs.set_active(self.roi_mode)
        if not self.roi_mode:
            self.canvas.draw()

    def toggle_draw_mode(self):
        if not self.main_window.image_loaded:
            return
        self.draw_mode = not self.draw_mode
        if self.draw_mode and self.roi_mode:
            self.toggle_roi_mode()
        self.main_window.add_log_entry("Draw selection mode: %s" % str(self.draw_mode))
        if self.draw_checkbox is not None:
            self.draw_checkbox.setChecked(self.draw_mode)
        self.ps.set_active(self.draw_mode)
        self.ps.set_visible(self.draw_mode)
        if not self.draw_mode:
            self.canvas.draw()

    def toggle_mask_mode(self):
        self.mask_mode = not self.mask_mode
        if self.imageplot_ref is None:
            return
        self.imageplot_ref.set_visible(self.mask_mode)
        self.canvas.draw()

    def roi_select_callback(self, eclick, erelease):
        a, b = int(self.rs.extents[0]), int(self.rs.extents[2])
        c, d = int(self.rs.extents[1]) - a, int(self.rs.extents[3]) - b
        self.rect = (a, b, c, d)

    def polygon_select_callback(self, verts):
        poly_path = Polypath(verts)
        for x in range(self.rect[0], self.rect[0] + self.rect[2]):
            for y in range(self.rect[1], self.rect[1] + self.rect[3]):
                if poly_path.contains_point((x, y)):
                    # Add your logic here to mark or process the points within the polygon
                    self.main_window.mask[y, x] = self.drawing_case
        self.update_mask()
        self.canvas.draw()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Central widget and primary layout
        central_widget = QtWidgets.QWidget(self)
        main_layout = QtWidgets.QVBoxLayout(central_widget)

        # Horizontal layout for the checkboxes and the MatplotlibWidget
        h_layout_main = QtWidgets.QHBoxLayout()
        # Create left side menu layout
        menu_layout = QtWidgets.QVBoxLayout()

        # Checkboxes for ROI and Drawing Modes
        self.roi_checkbox = QtWidgets.QCheckBox("ROI Mode")
        self.draw_checkbox = QtWidgets.QCheckBox("Drawing Mode")
        menu_layout.addWidget(self.roi_checkbox)
        menu_layout.addWidget(self.draw_checkbox)
        self.roi_checkbox.setDisabled(True)
        self.draw_checkbox.setDisabled(True)

        # Create the load image button
        self.clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(9, 9))
        self.image_loaded = False
        self.load_image_btn = QPushButton("Load Image/Video", self)
        self.load_image_btn.clicked.connect(self.load_and_plot_image)
        menu_layout.addWidget(self.load_image_btn)

        self.help_button = QPushButton("Help", self)
        self.help_button.clicked.connect(self.show_help_instructions)
        menu_layout.addWidget(self.help_button)

        # Create the "Save Mask" button
        self.save_mask_btn = QPushButton("Save Mask", self)
        self.save_mask_btn.clicked.connect(self.save_mask)
        menu_layout.addWidget(self.save_mask_btn)

        # Create a label for "Frame index:"
        frame_label = QtWidgets.QLabel("Frame index:", self)
        self.frame_spinbox = QSpinBox(self)
        self.frame_spinbox.valueChanged.connect(self.update_video_frame)
        frame_layout = QtWidgets.QHBoxLayout()
        frame_layout.addWidget(frame_label)
        frame_layout.addWidget(self.frame_spinbox)
        menu_layout.addLayout(frame_layout)
        self.frame_spinbox.setEnabled(False)

        # Create the terminal-like section
        self.log_terminal = QTextEdit(self)
        self.log_terminal.setReadOnly(True)
        menu_layout.addWidget(
            self.log_terminal
        )  # the 1 denotes the stretch factor, allocating space for the terminal

        # MatplotlibWidget
        h_layout_plots = QtWidgets.QHBoxLayout()
        self.plot1 = SegmentationWidget(
            roi_checkbox=self.roi_checkbox,
            draw_checkbox=self.draw_checkbox,
            main_window=self,
        )
        h_layout_plots.addWidget(self.plot1)

        h_layout_main.addLayout(
            menu_layout
        )  # Add checkboxes layout to the main horizontal layout
        h_layout_main.addLayout(h_layout_plots, 2)

        main_layout.addLayout(h_layout_main, 2)

        self.setCentralWidget(central_widget)
        self.resize(1200, 600)

    def show_help_instructions(self):
        instructions = (
            "Key '0' - To select areas of sure background\n"
            "Key '1' - To select areas of sure foreground\n"
            "Key '2' - To select areas of probable background\n"
            "Key '3' - To select areas of probable foreground\n"
            "\n"
            "Key 'n' - To update the segmentation\n"
            "Key 'r' - To reset the ROI\n"
            "Key 's' - To save the results\n"
            "Key 'c' - To clear the mask & ROI\n"
            "Key 'm' - To toggle the masked image"
        )

        QMessageBox.information(self, "Help", instructions)

    def load_and_plot_image(self):
        options = QFileDialog.Options()
        filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image/Video",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;Videos (*.mp4 *.avi);;All Files (*)",
            options=options,
        )
        if filePath:
            if filePath.endswith((".png", ".jpg", ".jpeg", ".bmp")):
                # Load the selected image file
                self.image_loaded = True
                self.image0 = cv.imread(filePath, 1)
            elif filePath.endswith((".mp4", ".avi")):
                # Load the selected video file
                self.video_loaded = True
                self.frame_spinbox.setEnabled(True)
                self.video = cv.VideoCapture(filePath)
                ret, self.image0 = self.video.read()
                total_frames = int(
                    self.video.get(cv.CAP_PROP_FRAME_COUNT)
                )  # Get the total number of frames
                self.frame_spinbox.setRange(
                    1, total_frames
                )  # Set the range of the QSpinBox

            self.image = CLAHE_normalize(self.image0, self.clahe)

            path, self.name, ext = splitfn(filePath)
            self.add_log_entry("Img: %s" % (self.name + ext))

            # plot image
            self.plot1.canvas.axes.clear()  # Clear previous plots
            self.plot1.canvas.axes.imshow(self.image[..., ::-1], origin="upper")

            # plot mask
            self.mask = np.zeros(self.image.shape[:2], dtype=np.uint8)
            self.plot1.canvas.ax2.clear()  # Clear previous plots
            self.plot1.maskplot_ref = None
            self.plot1.imageplot_ref = self.plot1.canvas.ax2.imshow(
                self.image[..., ::-1], origin="upper"
            )

            self.plot1.update_mask()
            self.plot1.canvas.draw()

    def save_mask(self):
        if not self.image_loaded:
            return
        # Prompt the user to choose a location to save the mask
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Mask",
            self.name + "_mask",
            "Images (*.png);;All Files (*)",
            options=options,
        )

        if file_path:
            # Save the mask as an image (you may need to convert it to 8-bit format)
            cv.imwrite(file_path, self.mask)
            self.add_log_entry("Mask saved to %s" % file_path)

    def update_video_frame(self, frame_number):
        if self.video_loaded:
            frame_number -= 1  # Adjust for 0-based indexing
            self.video.set(cv.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.video.read()
            if ret:
                self.image0 = frame
                self.image = CLAHE_normalize(self.image0, self.clahe)
                self.plot1.canvas.axes.clear()
                self.plot1.canvas.axes.imshow(self.image[..., ::-1], origin="upper")
                self.plot1.canvas.draw()

    def add_log_entry(self, entry):
        # Obtain all the log entries
        logs = self.log_terminal.toPlainText().split("\n")

        # Keep only the last 10 entries
        logs = logs[-9:] + [entry]

        # Update the terminal
        self.log_terminal.setText("\n".join(logs))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
