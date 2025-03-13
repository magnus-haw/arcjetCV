from arcjetCV.calibration.calibration_model import CalibrationModel
from arcjetCV.calibration.calibration_view import CalibrationView
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtPrintSupport import QPrinter, QPrintDialog
from matplotlib.backend_bases import cursors
import numpy as np
import cv2
import json
import os
from pathlib import Path
import shutil


class CalibrationController:
    def __init__(self, view: CalibrationView):
        self.view = view
        self.model = CalibrationModel()

        # Connect signals and slots
        self.view.load_button.clicked.connect(self.load_chessboard_images)
        self.view.calibrate_button.clicked.connect(self.calibrate_camera)
        self.view.print_button.clicked.connect(self.print_chessboard)
        self.view.load_image_button.clicked.connect(self.load_image)
        self.view.load_image_button_pattern.clicked.connect(self.load_image_diagonal)
        self.view.calculate_button.clicked.connect(self.calculate_ppcm)
        self.view.get_resolution_button.clicked.connect(self.calculate_ppcm)
        self.view.save_calibration_button.clicked.connect(self.save_calibration)

        # Initialize variables
        self.image_paths = []
        self.image = None
        self.start_point = None
        self.line = None
        self.line_artist = None

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

    def detect_pattern(self, img, pattern_size):
        """
        Detect whether the image contains a chessboard or a circles grid.

        Args:
            img (numpy.ndarray): The grayscale image to analyze.
            pattern_size (tuple): Chessboard pattern size (columns, rows).
            pattern_size (tuple): Circles grid pattern size (columns, rows).

        Returns:
            tuple: (str, object_points, image_points)
                str: "chessboard", "circles_grid", or None.
                object_points: 3D points in real-world space.
                image_points: 2D points in the image plane.
        """
        # Prepare 3D object points for chessboard and circles grid
        chessboard_obj_points = np.zeros(
            (pattern_size[0] * pattern_size[1], 3), np.float32
        )
        chessboard_obj_points[:, :2] = np.mgrid[
            0 : pattern_size[0], 0 : pattern_size[1]
        ].T.reshape(-1, 2)

        circles_obj_points = np.zeros(
            (pattern_size[0] * pattern_size[1], 3), np.float32
        )
        circles_obj_points[:, :2] = np.mgrid[
            0 : pattern_size[0], 0 : pattern_size[1]
        ].T.reshape(-1, 2)

        # Try detecting chessboard pattern
        ret_chessboard, corners_chessboard = cv2.findChessboardCorners(
            img, pattern_size
        )
        if ret_chessboard:
            return "chessboard", chessboard_obj_points, corners_chessboard

        # Try detecting circles grid pattern
        ret_circles_grid, centers_circles_grid = cv2.findCirclesGrid(
            img, pattern_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID
        )
        if ret_circles_grid:
            return "circles_grid", circles_obj_points, centers_circles_grid

        # No pattern detected
        return None, None, None

    def _generate_object_points(self, pattern_size, pattern_type):
        """
        Generates 3D object points for a given pattern.

        Args:
            pattern_size (tuple): The pattern size (columns, rows).
            pattern_type (str): Type of pattern ("chessboard", "circles_grid", "asymmetric_circles_grid").

        Returns:
            numpy.ndarray: 3D object points.
        """
        obj_points = np.zeros((pattern_size[0] * pattern_size[1], 3), np.float32)

        if pattern_type == "chessboard" or pattern_type == "circles_grid":
            obj_points[:, :2] = np.mgrid[
                0 : pattern_size[0], 0 : pattern_size[1]
            ].T.reshape(-1, 2)

        elif pattern_type == "asymmetric_circles_grid":
            obj_points[:, :2] = np.array(
                [
                    [(x, y + 0.5 * (x % 2)) for x in range(pattern_size[0])]
                    for y in range(pattern_size[1])
                ]
            ).reshape(-1, 2)

        return obj_points

    def detect_pattern(self, img, pattern_size):
        """
        Detects whether the image contains a chessboard or a circle grid (symmetric or asymmetric).

        Args:
            img (numpy.ndarray): Grayscale image.
            pattern_size (tuple): The pattern size (columns, rows).

        Returns:
            tuple: (str, object_points, image_points)
                str: "chessboard", "circles_grid", "asymmetric_circles_grid", or None.
                object_points: 3D real-world points.
                image_points: 2D image points.
        """

        # Enhance contrast for better detection
        img = cv2.equalizeHist(img)

        # 1️⃣ Detect Chessboard Pattern
        found_chessboard, corners_chessboard = cv2.findChessboardCorners(
            img, pattern_size
        )
        if found_chessboard:
            return (
                "chessboard",
                self._generate_object_points(pattern_size, "chessboard"),
                corners_chessboard,
            )

        # 2️⃣ Detect Symmetric Circles Grid
        found_circles_grid, centers_circles_grid = cv2.findCirclesGrid(
            img, pattern_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID
        )
        if found_circles_grid:
            return (
                "circles_grid",
                self._generate_object_points(pattern_size, "circles_grid"),
                centers_circles_grid,
            )

        # 3️⃣ Detect Asymmetric Circles Grid
        found_asymmetric_grid, centers_asymmetric_grid = cv2.findCirclesGrid(
            img, pattern_size, flags=cv2.CALIB_CB_ASYMMETRIC_GRID
        )
        if found_asymmetric_grid:
            return (
                "asymmetric_circles_grid",
                self._generate_object_points(pattern_size, "asymmetric_circles_grid"),
                centers_asymmetric_grid,
            )
        result = self.found_asym_pattern_2(img, pattern_size, 3000, 15000)
        if result[0] is not None:
            return result

        # 4️⃣ Custom asymmetric pattern detection - Second Attempt
        return self.found_asym_pattern_2(img, pattern_size, 500, 3000)
        # ❌ No pattern detected
        # return None, None, None

    def asym_obj_points(self, rows, cols):
        circles_obj_points = np.zeros((rows * cols, 3), np.float32)
        circles_obj_points[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2)

        for col in range(1, cols, 2):
            col_arr = np.arange(0, rows)
            inds = col * rows + col_arr
            for j in inds:
                circles_obj_points[j, 0] += 0.5
        return circles_obj_points

    def found_asym_pattern_2(self, img, pattern_size, minArea, maxArea):
        """
        Custom asymmetric circle grid detection using a blob detector.
        Used as a fallback when `cv2.findCirclesGrid` fails.

        Args:
            img (numpy.ndarray): Grayscale image.
            pattern_size (tuple): The pattern size (columns, rows).

        Returns:
            tuple: (str, object_points, image_points) or (None, None, None) if detection fails.
        """

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

        # Configure the SimpleBlobDetector for better circle detection
        blobParams = cv2.SimpleBlobDetector_Params()
        blobParams.minThreshold = 35
        blobParams.maxThreshold = 185
        blobParams.filterByArea = True
        blobParams.minArea = minArea
        blobParams.maxArea = maxArea

        blobParams.filterByCircularity = True
        blobParams.minCircularity = 0.25
        blobParams.filterByConvexity = True
        blobParams.minConvexity = 0.75
        blobParams.filterByInertia = True
        blobParams.minInertiaRatio = 0.01
        blobDetector = cv2.SimpleBlobDetector_create(blobParams)

        # Generate expected object points
        objp = self.asym_obj_points(
            pattern_size[1], pattern_size[0]
        )  # Ensure (rows, cols) order

        # Preprocess the image for better blob detection
        blurred = cv2.GaussianBlur(img, (15, 15), 0)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(blurred)
        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        sharpened = cv2.filter2D(clahe_img, -1, kernel)

        # Detect keypoints using the blob detector
        keypoints = blobDetector.detect(sharpened)

        if not keypoints:
            print("❌ No keypoints found, asymmetric grid detection failed.")
            return None, None, None

        # Convert keypoints to a usable format for cv2.findCirclesGrid
        im_with_keypoints = cv2.drawKeypoints(
            img,
            keypoints,
            np.array([]),
            (0, 255, 0),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )
        im_with_keypoints_gray = cv2.cvtColor(im_with_keypoints, cv2.COLOR_BGR2GRAY)

        # Try detecting circles again after preprocessing
        ret, corners = cv2.findCirclesGrid(
            img,
            pattern_size,
            flags=(cv2.CALIB_CB_ASYMMETRIC_GRID + cv2.CALIB_CB_CLUSTERING),
            blobDetector=blobDetector,
        )

        if not ret:
            print("❌ Custom asymmetric detection failed.")
            return None, None, None

        # Refine detected corners
        corners2 = cv2.cornerSubPix(
            im_with_keypoints_gray, corners, (11, 11), (-1, -1), criteria
        )

        return "asymmetric_circles_grid", objp, corners2

    def save_to_json(self, calibration_data, file_path="calibration_results.json"):
        """
        Save calibration parameters to a JSON file.

        Args:
            calibration_data (dict): Calibration parameters.
            file_path (str): Path to save the JSON file.

        Returns:
            tuple: (bool, str) Success status and error message.
        """
        try:
            # Get the directory of the current script
            script_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_directory, file_path)

            # Check if the file exists and load existing data
            if os.path.exists(file_path):
                with open(file_path, "r") as json_file:
                    existing_data = json.load(json_file)
            else:
                existing_data = {}

            # Update with new data
            existing_data.update(calibration_data)

            # Write the updated data back to the file
            with open(file_path, "w") as json_file:
                json.dump(existing_data, json_file, indent=4)

            print(str(file_path))

            return True, None
        except Exception as e:
            return False, str(e)

    def calculate_3d_orientation(
        self, obj_points, img_points, camera_matrix, dist_coeffs
    ):
        """
        Calculate the 3D orientation using the rotation and translation vectors.
        Args:
            obj_points (list): List of 3D object points.
            img_points (list): List of 2D image points.
            camera_matrix (numpy.ndarray): Camera intrinsic matrix.
            dist_coeffs (numpy.ndarray): Distortion coefficients.
        Returns:
            tuple: Rotation matrix, translation vector, and Euler angles.
        """
        ret, rvec, tvec = cv2.solvePnP(
            obj_points, img_points, camera_matrix, dist_coeffs
        )
        if not ret:
            QMessageBox.warning(self.view, "Error", "3D Pose estimation failed.")
            return None

        # Convert rotation vector to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rvec)

        # Convert rotation matrix to Euler angles
        theta_x = np.degrees(np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2]))
        theta_y = np.degrees(
            np.arctan2(
                -rotation_matrix[2, 0],
                np.sqrt(rotation_matrix[2, 1] ** 2 + rotation_matrix[2, 2] ** 2),
            )
        )
        theta_z = np.degrees(np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0]))

        return rotation_matrix, tvec, (theta_x, theta_y, theta_z)

    def calculate_2d_affine_matrix(self, obj_points, img_points):
        """
        Computes an affine transformation matrix for 2D correction.

        Args:
            obj_points (numpy.ndarray): 2D object points in reference frame.
            img_points (numpy.ndarray): 2D detected points in the image.

        Returns:
            numpy.ndarray: 2D affine transformation matrix (if successful).
        """
        if len(obj_points) < 3 or len(img_points) < 3:
            print("❌ ERROR: At least 3 points are required for affine transformation.")
            return None

        # Compute affine transformation
        affine_matrix, _ = cv2.estimateAffinePartial2D(obj_points, img_points)

        if affine_matrix is None:
            print("❌ ERROR: Affine transformation failed.")
        return affine_matrix

    def calibrate_camera(self):
        """Perform full 3D camera calibration and save results."""
        if not self.image_paths:
            QMessageBox.warning(
                self.view, "Error", "Please load images for calibration first."
            )
            return

        pattern_size = (
            self.view.grid_cols_input.value(),
            self.view.grid_rows_input.value(),
        )
        obj_points = []
        img_points = []

        for img_path in self.image_paths:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                QMessageBox.warning(
                    self.view, "Error", f"Failed to load image: {img_path}"
                )
                return

            # Detect pattern
            pattern_type, obj_p, img_p = self.detect_pattern(
                img, pattern_size, pattern_size
            )
            if pattern_type:
                obj_points.append(obj_p)
                img_points.append(img_p)
            else:
                QMessageBox.warning(
                    self.view, "Error", f"No pattern detected in {img_path}"
                )
                return

        # Perform camera calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points, img_points, img.shape[::-1], None, None
        )
        if not ret:
            QMessageBox.warning(self.view, "Error", "Camera calibration failed.")
            return

        # Calculate 3D orientation
        rotation_matrix, tvec, euler_angles = self.calculate_3d_orientation(
            obj_points[0], img_points[0], mtx, dist
        )

        # Calculate 2D affine transformation
        affine_matrix = self.calculate_2d_affine_matrix(
            obj_points[0][:, :2], img_points[0][:, 0, :]
        )  # Convert 3D to 2D points

        # Store calibration data
        calibration_data = {
            "camera_matrix": mtx.tolist(),
            "dist_coeffs": dist.tolist(),
            "rvec": rvecs[0].tolist() if rvecs else None,
            "tvec": tvecs[0].tolist() if tvecs else None,
            "affine_matrix": (
                affine_matrix.tolist() if affine_matrix is not None else None
            ),
        }

        # Save calibration data to file
        success, save_error = self.save_to_json(calibration_data)
        if success:
            self.calibration_data = {
                "camera_matrix": np.array(
                    calibration_data["camera_matrix"], dtype=np.float32
                ),
                "dist_coeffs": np.array(
                    calibration_data["dist_coeffs"], dtype=np.float32
                ),
                "rvec": (
                    np.array(calibration_data["rvec"], dtype=np.float32)
                    if calibration_data["rvec"]
                    else None
                ),
                "tvec": (
                    np.array(calibration_data["tvec"], dtype=np.float32)
                    if calibration_data["tvec"]
                    else None
                ),
                "affine_matrix": (
                    np.array(calibration_data["affine_matrix"], dtype=np.float32)
                    if calibration_data["affine_matrix"]
                    else None
                ),
            }
            self.calibrated = True
            QMessageBox.information(
                self.view,
                "Success",
                "3D and 2D Camera calibration successful and saved.",
            )
        else:
            self.calibration_data = None
            self.calibrated = False
            QMessageBox.warning(
                self.view, "Error", f"Failed to save calibration: {save_error}"
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
        """Display the loaded image and enable dynamic line drawing."""
        self.view.figure.clear()
        self.ax = self.view.figure.add_subplot(111)
        self.ax.imshow(self.image)
        self.ax.set_title("Click and drag to draw a line")
        self.ax.figure.canvas.set_cursor(cursors.SELECT_REGION)
        self.view.canvas.draw()

        # Initialize dynamic line variables
        self.line_artist = None

        # Connect mouse events
        self.cid_press = self.view.canvas.mpl_connect(
            "button_press_event", self.on_mouse_press
        )
        self.cid_release = self.view.canvas.mpl_connect(
            "button_release_event", self.on_mouse_release
        )
        self.cid_motion = self.view.canvas.mpl_connect(
            "motion_notify_event", self.on_mouse_motion
        )

    def on_mouse_press(self, event):
        """Record the start point of the line."""
        if event.inaxes != self.ax:
            return
        self.start_point = (event.xdata, event.ydata)

        # Clear previous line if it exists
        if self.line_artist:
            self.line_artist.remove()
            self.line_artist = None
        self.view.canvas.draw()

    def on_mouse_motion(self, event):
        """Update the line dynamically as the mouse moves."""
        if event.inaxes != self.ax or not self.start_point:
            return

        # Clear the previous line
        if self.line_artist:
            self.line_artist.remove()

        # Draw a new line from the start point to the current mouse position
        end_point = (event.xdata, event.ydata)
        (self.line_artist,) = self.ax.plot(
            [self.start_point[0], end_point[0]],
            [self.start_point[1], end_point[1]],
            color="red",
            linewidth=2,
        )
        self.view.canvas.draw()

    def on_mouse_release(self, event):
        """Finalize the line when the mouse button is released."""
        if event.inaxes != self.ax or not self.start_point:
            return

        # Record the end point
        end_point = (event.xdata, event.ydata)
        self.line = (self.start_point, end_point)

        # Draw the final line
        if self.line_artist:
            self.line_artist.remove()
        (self.line_artist,) = self.ax.plot(
            [self.start_point[0], end_point[0]],
            [self.start_point[1], end_point[1]],
            color="red",
            linewidth=2,
        )

        self.view.canvas.draw()
        self.start_point = None  # Reset the start point

    def load_image_diagonal(self):
        """Load an image, autodetect a chessboard or circular pattern, and plot its diagonal."""
        # Open file dialog to load an image
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Load Image for Pattern Detection",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )
        if not file_path:
            QMessageBox.warning(self.view, "Error", "No image selected.")
            return

        # Load and convert the image
        self.image = cv2.imread(file_path)
        if self.image is None:
            QMessageBox.warning(self.view, "Error", "Unable to load the image.")
            return
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)

        # Define grid sizes
        pattern_size = (
            self.view.grid_cols_input.value(),
            self.view.grid_rows_input.value(),
        )

        # Detect the pattern
        pattern_type, obj_points, corners = self.detect_pattern(gray, pattern_size)
        if pattern_type is None:
            QMessageBox.warning(self.view, "Error", "No valid pattern detected.")
            return

        # Draw detected pattern
        if pattern_type == "chessboard":
            cv2.drawChessboardCorners(self.image, pattern_size, corners, True)
        elif pattern_type == "circles_grid":
            cv2.drawChessboardCorners(self.image, pattern_size, corners, True)

        # Calculate diagonal endpoints
        top_left = corners[0][0]  # Top-left corner
        bottom_right = corners[-1][0]  # Bottom-right corner

        # Plot diagonal on Matplotlib canvas
        self.view.figure.clear()
        self.ax = self.view.figure.add_subplot(111)
        self.ax.imshow(cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB))
        self.ax.plot(
            [top_left[0], bottom_right[0]],
            [top_left[1], bottom_right[1]],
            color="red",
            linewidth=2,
            label="Diagonal",
        )
        self.ax.scatter(
            [top_left[0], bottom_right[0]],
            [top_left[1], bottom_right[1]],
            color="yellow",
            s=100,
        )
        self.ax.set_title(f"Detected {pattern_type.capitalize()} and Diagonal")
        self.ax.legend()
        self.view.canvas.draw()

        # Calculate diagonal length
        self.diagonal_distance = np.linalg.norm(top_left - bottom_right)
        QMessageBox.information(
            self.view,
            "Diagonal Length",
            f"Diagonal Distance: {self.diagonal_distance:.2f} pixels",
        )

    def calculate_ppcm(self):
        """
        Calculate pixels per mm based on the current tab:
        - Pattern Resolution: Use diagonal distance.
        - Ruler Resolution: Use manually drawn line.
        """
        if self.image is None:
            QMessageBox.warning(self.view, "Error", "Please load an image first.")
            return

        # Determine the selected tab
        current_tab_index = self.view.resolution_tabs.currentIndex()

        if current_tab_index == 0:  # Pattern Resolution Tab
            # Use diagonal distance
            try:
                real_length = (
                    self.view.diagonal_distance_value.value()
                )  # Get value from QDoubleSpinBox
                if not hasattr(self, "diagonal_distance"):
                    QMessageBox.warning(
                        self.view, "Error", "Diagonal distance not calculated yet."
                    )
                    return

                self.ppm = self.diagonal_distance / real_length
                self.view.ppcm_label.setText(f"Pixels per mm: {self.ppm:.2f}")
            except ValueError:
                QMessageBox.warning(
                    self.view, "Error", "Invalid real-world length entered."
                )
        elif current_tab_index == 1:  # Ruler Resolution Tab
            # Use manually drawn line
            if not self.line:
                QMessageBox.warning(
                    self.view, "Error", "Please draw a line on the image."
                )
                return

            # Compute pixel length of the line
            pixel_length = np.linalg.norm(
                np.array(self.line[1]) - np.array(self.line[0])
            )

            try:
                real_length = float(self.view.distance_input.text())
                self.ppm = pixel_length / real_length
                self.view.ppcm_label.setText(f"Pixels per mm: {self.ppm:.2f}")
            except ValueError:
                QMessageBox.warning(
                    self.view, "Error", "Invalid real-world length entered."
                )
        else:
            QMessageBox.warning(self.view, "Error", "Unknown tab selected.")
            return

        # Save ppm to the JSON file
        self.save_ppm_to_json()

    def save_ppm_to_json(
        self,
        file_path=os.path.join(
            Path(__file__).parent.absolute(), "calibration_results.json"
        ),
    ):
        """
        Save the calculated ppm value to the calibration JSON file.

        Args:
            file_path (str): Path to the JSON file.
        """
        if not hasattr(self, "ppm") or self.ppm is None:
            QMessageBox.warning(self.view, "Error", "No valid ppm value to save.")
            return

        try:
            # Convert self.ppm to a standard Python float
            ppm_value = float(self.ppm)

            # Check if the file exists and load existing data
            if os.path.exists(file_path):
                with open(file_path, "r") as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        # Handle invalid or empty JSON file
                        existing_data = {}
            else:
                existing_data = {}

            # Update or create the "pixels_per_mm" key
            existing_data["pixels_per_mm"] = ppm_value

            # Write the updated data back to the file
            with open(file_path, "w") as json_file:
                json.dump(existing_data, json_file, indent=4)

            QMessageBox.information(
                self.view, "Success", "Pixels per mm saved successfully to JSON."
            )
        except Exception as e:
            QMessageBox.warning(
                self.view, "Error", f"Failed to save pixels per mm: {str(e)}"
            )

    def save_calibration(self):
        """Prompts the user to select a filename and duplicates calibration.json to that file."""
        default_filename = "calibration_copy.json"

        # Open file dialog for user to choose where to save the file
        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Calibration", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:  # If user selected a file
            source_file = os.path.join(
                Path(__file__).parent.absolute(), "calibration_results.json"
            )
            try:
                # Copy content from calibration.json
                shutil.copy(source_file, file_path)
                QMessageBox.information(
                    self, "Success", f"Calibration saved as {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save calibration: {e}")

    def apply_calibration(frame, calibration_data):
        """
        Apply calibration to a single frame using provided calibration data.

        Args:
            frame (numpy.ndarray): The input frame (image) to calibrate.
            calibration_data (dict): A dictionary containing calibration data with keys:
                - "camera_matrix": The intrinsic camera matrix.
                - "dist_coeffs": The distortion coefficients.
                - "affine_matrix" (optional): A 2D affine transformation matrix.

        Returns:
            numpy.ndarray: The calibrated frame (image).
        """
        # Extract calibration data
        camera_matrix = np.array(calibration_data["camera_matrix"])
        dist_coeffs = np.array(calibration_data["dist_coeffs"])

        # Undistort the frame
        h, w = frame.shape[:2]
        new_camera_matrix, _ = cv2.getOptimalNewCameraMatrix(
            camera_matrix, dist_coeffs, (w, h), 1, (w, h)
        )
        undistorted_frame = cv2.undistort(
            frame, camera_matrix, dist_coeffs, None, new_camera_matrix
        )

        # Check if affine transformation is available
        if "affine_matrix" in calibration_data:
            affine_matrix = np.array(calibration_data["affine_matrix"])

            # Extract rotation angle from affine transformation
            angle_rad = np.arctan2(affine_matrix[1, 0], affine_matrix[0, 0])
            angle_deg = np.degrees(angle_rad)  # Convert to degrees

            # Show warning if angle correction is greater than 8 degrees
            if abs(angle_deg) > 8:
                QMessageBox.warning(
                    None,
                    "Warning",
                    f"⚠️ High rotation correction detected: {angle_deg:.2f}°.\n"
                    "Please verify the calibration data.",
                )

            # Apply the affine transformation
            return cv2.warpAffine(undistorted_frame, affine_matrix, (w, h))

        # Return undistorted frame if no affine transformation is applied
        return undistorted_frame

        # if "rvec" in calibration_data and "tvec" in calibration_data:
        #     rvec = np.array(calibration_data["rvec"], dtype=np.float32).reshape(3, 1)
        #     tvec = np.array(calibration_data["tvec"], dtype=np.float32).reshape(3, 1)

        #     # Define object points (assuming a flat image plane)
        #     height, width = undistorted_frame.shape[:2]
        #     object_points = np.array(
        #         [[0, 0, 0], [width, 0, 0], [width, height, 0], [0, height, 0]],
        #         dtype=np.float32,
        #     )

        #     # Project 3D points to 2D image coordinates
        #     success, image_points = cv2.projectPoints(
        #         object_points, rvec, tvec, new_camera_matrix, None
        #     )

        #     if not success or image_points is None or np.isnan(image_points).any():
        #         print(
        #             "❌ ERROR: Invalid projected points. Skipping perspective transform."
        #         )
        #         return undistorted_frame

        #     # Compute perspective transform
        #     src_points = np.float32([[0, 0], [width, 0], [width, height], [0, height]])
        #     dst_points = np.float32(image_points[:, 0, :])  # Ensure correct shape
        #     perspective_transform = cv2.getPerspectiveTransform(src_points, dst_points)

        #     if np.isnan(perspective_transform).any():
        #         print("❌ ERROR: Perspective transform contains NaN values.")
        #         return undistorted_frame

        #     # Apply the transformation
        #     calibrated_frame = cv2.warpPerspective(
        #         undistorted_frame, perspective_transform, (width, height)
        #     )

        #     if np.all(calibrated_frame == 0):
        #         print(
        #             "❌ ERROR: Warping failed, resulting in a black image. Returning undistorted frame."
        #         )
        #         return undistorted_frame

        #     return calibrated_frame
        # else:
        #     print("ℹ️ INFO: No 3D transformation applied, returning undistorted frame.")
        #     return undistorted_frame
