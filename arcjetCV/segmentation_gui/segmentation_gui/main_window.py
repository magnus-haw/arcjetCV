import sys
import cv2
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QCheckBox,
    QHBoxLayout,
    QMessageBox,
)
from PySide6.QtCore import Qt
from .matplotlib_widget import MatplotlibWidget
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QSizePolicy,
    QFrame,
)
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QFileDialog,
    QLabel,
    QSizePolicy,
    QFrame,
    QSpinBox,
)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle("Segment Anything Cool")
        self.setGeometry(100, 100, 800, 600)

        main_widget = QWidget(self)
        self.setCentralWidget(main_widget)

        # Create a horizontal layout to organize buttons and the MatplotlibWidget
        layout = QHBoxLayout(main_widget)

        # Create a vertical layout for the buttons on the left
        button_layout = QVBoxLayout()
        # Set size policy for the button_layout to Fixed

        load_button = QPushButton("Load Image/Video", main_widget)
        button_layout.addWidget(load_button)
        load_button.clicked.connect(self.load_image)

        # Create a checkbox for 'SAM'
        self.sam_checkbox = QCheckBox("SAM", main_widget)
        button_layout.addWidget(self.sam_checkbox)

        # Create a checkbox for 'GrabCut'
        self.grabcut_checkbox = QCheckBox("GrabCut", main_widget)
        button_layout.addWidget(self.grabcut_checkbox)

        # Create a frame to hold the Confirm and Undo buttons
        button_frame = QFrame(main_widget)
        button_frame_layout = QVBoxLayout(button_frame)
        # Create a QHBoxLayout for the label and spinbox
        video_index_layout = QHBoxLayout()

        # Create a QLabel for 'Video frame index:'
        video_index_label = QLabel("Video frame index:", main_widget)
        video_index_layout.addWidget(video_index_label)

        # Create a QSpinBox for selecting video frames
        self.frame_spinbox = QSpinBox(main_widget)
        self.frame_spinbox.setRange(
            1, 1
        )  # Initial range, update it when a video is loaded
        self.frame_spinbox.setEnabled(False)  # Initially disabled

        video_index_layout.addWidget(self.frame_spinbox)
        self.frame_spinbox.valueChanged.connect(self.update_video_frame)

        # Add the QHBoxLayout with label and spinbox to the button_frame_layout
        button_frame_layout.addLayout(video_index_layout)

        # Create a button to confirm the current label and create a new one
        self.create_new = QPushButton("Confirm and Create New Mask", button_frame)
        button_frame_layout.addWidget(self.create_new)
        self.create_new.clicked.connect(self.confirm_and_new)
        self.create_new.setEnabled(False)

        self.confirm_button = QPushButton("Confirm Label", button_frame)
        button_frame_layout.addWidget(self.confirm_button)
        self.confirm_button.clicked.connect(self.confirm_label)
        self.confirm_button.setEnabled(False)

        # Create a button to undo a point
        self.undo_button = QPushButton("Undo", button_frame)
        button_frame_layout.addWidget(self.undo_button)
        self.undo_button.clicked.connect(self.undo)
        self.undo_button.setEnabled(False)

        # Add the button frame to the button layout
        button_layout.addWidget(button_frame)

        self.save_button = QPushButton("Save Mask", main_widget)
        button_layout.addWidget(self.save_button)
        self.save_button.clicked.connect(self.save_mask)
        self.save_button.setEnabled(False)

        # Add a stretchable space at the bottom of button_layout to align buttons to the top
        button_layout.addStretch()

        # Create a new vertical layout for aligning the button_layout at the top
        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(button_layout)

        # Create a container widget for the vertical_layout
        vertical_container = QWidget()
        vertical_container.setLayout(vertical_layout)
        vertical_container.setFixedWidth(300)  # Adjust the width as needed

        # Add the button_layout with alignment and spacing to the main layout
        layout.addWidget(vertical_container)
        layout.addSpacing(20)  # Add some spacing between buttons and MatplotlibWidget
        self.matplotlib_widget = MatplotlibWidget(main_widget)
        self.matplotlib_widget.setFocusPolicy(Qt.StrongFocus)
        layout.addWidget(self.matplotlib_widget)

    def load_image(self):
        options = QFileDialog.Options()
        self.filePath, _ = QFileDialog.getOpenFileName(
            self,
            "Load Image/Video",
            "",
            "Images (*.png *.jpg *.jpeg *.bmp);;Videos (*.mp4 *.avi);;All Files (*)",
            options=options,
        )
        if self.filePath:
            if self.filePath.endswith((".png", ".jpg", ".jpeg", ".bmp")):
                # Load the selected image file                self.image_loaded = True
                image0 = cv2.imread(self.filePath)

            elif self.filePath.endswith((".mp4", ".avi")):
                # Load the selected video file
                self.video_loaded = True
                self.frame_spinbox.setEnabled(True)
                self.video = cv2.VideoCapture(self.filePath)
                ret, image0 = self.video.read()
                total_frames = int(
                    self.video.get(cv2.CAP_PROP_FRAME_COUNT)
                )  # Get the total number of frames
                self.frame_spinbox.setRange(
                    1, total_frames
                )  # Set the range of the QSpinBox

            self.matplotlib_widget.setup_segmenter(
                image0, self.filePath, self.matplotlib_widget
            )
            # Enable or disable buttons based on whether an image or video is loaded
            self.confirm_button.setEnabled(True)
            self.create_new.setEnabled(True)
            self.undo_button.setEnabled(True)
            self.save_button.setEnabled(True)

    def update_video_frame(self, frame_number):
        if self.video_loaded:
            frame_number -= 1  # Adjust for 0-based indexing
            self.video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = self.video.read()
            if ret:
                self.image0 = frame
                self.matplotlib_widget.setup_segmenter(
                    self.image0, self.filePath, self.matplotlib_widget
                )

    def confirm_and_new(self):
        self.matplotlib_widget.segmenter.new_tow()

    def confirm_label(self):
        self.matplotlib_widget.segmenter.label_ok()

    def undo(self):
        self.matplotlib_widget.segmenter.undo()

    def save_mask(self):
        options = QFileDialog.Options()

        # Suggest a default file name based on the frame name
        suggested_name = (
            os.path.splitext(os.path.basename(self.filePath))[0] + "_mask.png"
        )
        save_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Mask",
            suggested_name,
            "Images (*.png *.jpg);;All Files (*)",
            options=options,
        )

        if save_path:
            self.matplotlib_widget.segmenter.save_annotation(save_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())
