from arcjetCV.calibration.calibration_model import CalibrationModel
from arcjetCV.calibration.calibration_view import CalibrationView
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
import numpy as np
import cv2


class CalibrationController:
    def __init__(self, view: CalibrationView):
        self.view = view
        self.model = CalibrationModel()

        # Connect signals and slots
        self.view.load_button.clicked.connect(self.load_chessboard_images)
        self.view.calibrate_button.clicked.connect(self.calibrate_camera)
        self.view.print_button.clicked.connect(self.print_chessboard)
        self.view.load_image_button.clicked.connect(self.load_image)
        self.view.calculate_button.clicked.connect(self.calculate_ppcm)

        # Initialize variables
        self.image_paths = []
        self.image = None
        self.start_point = None
        self.line = None

        # Connect Matplotlib canvas events
        self.cid_press = None
        self.cid_release = None

    def load_chessboard_images(self):
        """Load chessboard images for camera calibration."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self.view, "Select Chessboard Images", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_paths:
            self.image_paths = file_paths
            self.view.image_label.setText(f"{len(file_paths)} images loaded")
        else:
            self.view.image_label.setText("No images loaded")

    def calibrate_camera(self):
        """Perform camera calibration using loaded chessboard images."""
        if not self.image_paths:
            QMessageBox.warning(
                self.view, "Error", "Please load chessboard images first."
            )
            return

        ret, error = self.model.calibrate_camera(
            self.image_paths, (9, 6), 1.0  # Chessboard size and square size
        )

        if not ret:
            QMessageBox.warning(self.view, "Error", error or "Calibration failed.")
        else:
            success, save_error = self.model.save_calibration()
            if success:
                QMessageBox.information(
                    self.view, "Success", "Camera calibration successful and saved."
                )
            else:
                QMessageBox.warning(
                    self.view,
                    "Error",
                    f"Calibration saved but encountered: {save_error}",
                )

    def print_chessboard(self):
        """Generate and print a chessboard pattern."""
        filename = "chessboard_pattern.png"
        rows, cols, square_size = 9, 6, 50  # Default values
        image_size = (cols * square_size, rows * square_size)

        # Generate chessboard
        chessboard = np.ones((image_size[1], image_size[0]), dtype=np.uint8) * 255
        for i in range(rows):
            for j in range(cols):
                if (i + j) % 2 == 0:
                    x_start = j * square_size
                    y_start = i * square_size
                    chessboard[
                        y_start : y_start + square_size, x_start : x_start + square_size
                    ] = 0

        cv2.imwrite(filename, chessboard)

        # Print using QPrinter
        printer = QPrinter()
        print_dialog = QFileDialog(printer)
        if print_dialog.exec() == QFileDialog.Accepted:
            image = QImage(filename)
            painter = QPainter(printer)
            rect = painter.viewport()
            size = image.size()
            size.scale(rect.size(), Qt.KeepAspectRatio)
            painter.setViewport(rect.x(), rect.y(), size.width(), size.height())
            painter.setWindow(image.rect())
            painter.drawImage(0, 0, image)
            painter.end()
            QMessageBox.information(
                self.view, "Success", f"{filename} printed successfully."
            )
        else:
            QMessageBox.information(self.view, "Cancelled", "Printing cancelled.")

    def load_image(self):
        """Load an image for resolution measurement."""
        file_path, _ = QFileDialog.getOpenFileName(
            self.view, "Load Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.image = cv2.imread(file_path)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
            self.display_image()
        else:
            QMessageBox.warning(self.view, "Error", "No image selected.")

    def display_image(self):
        """Display the loaded image and enable line drawing."""
        self.view.figure.clear()
        self.ax = self.view.figure.add_subplot(111)
        self.ax.imshow(self.image)
        self.ax.set_title("Click and drag to draw a line")
        self.view.canvas.draw()

        # Connect mouse events
        self.cid_press = self.view.canvas.mpl_connect(
            "button_press_event", self.on_mouse_press
        )
        self.cid_release = self.view.canvas.mpl_connect(
            "button_release_event", self.on_mouse_release
        )

    def on_mouse_press(self, event):
        """Record the start point of a line."""
        if event.inaxes != self.ax:
            return
        self.start_point = (event.xdata, event.ydata)

    def on_mouse_release(self, event):
        """Record the end point and draw a line."""
        if event.inaxes != self.ax or not self.start_point:
            return

        end_point = (event.xdata, event.ydata)
        self.line = (self.start_point, end_point)

        # Draw the line on the image
        self.ax.plot(
            [self.start_point[0], end_point[0]],
            [self.start_point[1], end_point[1]],
            color="red",
        )
        self.view.canvas.draw()

    def calculate_ppcm(self):
        """Calculate pixels per mm based on the drawn line."""
        if self.image is None:
            QMessageBox.warning(self.view, "Error", "Please load an image first.")
            return

        if not self.line:
            QMessageBox.warning(self.view, "Error", "Please draw a line on the image.")
            return

        # Compute pixel length of the line
        pixel_length = np.linalg.norm(np.array(self.line[1]) - np.array(self.line[0]))

        # Get real-world length in cm
        try:
            real_length_cm = float(self.view.cm_input.text())
            ppm = pixel_length / (real_length_cm * 10)  # Convert cm to mm
            self.view.ppcm_label.setText(f"Pixels per mm: {ppm:.2f}")
        except ValueError:
            QMessageBox.warning(
                self.view, "Error", "Invalid real-world length entered."
            )
