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

    def _generate_object_points(self, pattern_size, pattern_type, spacing=1.0):
        """
        Generates 3D object points for a given pattern with real-world spacing.

        Args:
            pattern_size (tuple): The pattern size (columns, rows).
            pattern_type (str): Type of pattern.
            spacing (float): Real-world spacing between points in meters (default: 1.0)

        Returns:
            numpy.ndarray: 3D object points.
        """
        cols, rows = pattern_size
        if pattern_type in ["chessboard", "circles_grid"]:
            obj_points = np.zeros((rows * cols, 3), np.float32)
            obj_points[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
            obj_points *= spacing
        elif pattern_type == "asymmetric_circles_grid":
            obj_points = []
            for i in range(rows):
                for j in range(cols):
                    x = (2 * j + i % 2) * spacing / 2.0
                    y = i * spacing
                    obj_points.append([x, y, 0])
            obj_points = np.array(obj_points, dtype=np.float32).reshape(-1, 1, 3)
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

    def calculate_2d_affine_matrix(self, img, obj_points, img_points):
        """
        Computes an affine transformation matrix for 2D correction.

        Args:
            obj_points (numpy.ndarray): 2D object points in reference frame.
            img_points (numpy.ndarray): 2D detected points in the image.

        Returns:
            numpy.ndarray: 2D affine transformation matrix (if successful), else None.
        """
        obj_points = np.asarray(obj_points, dtype=np.float32).reshape(-1, 2)
        img_points = np.asarray(img_points, dtype=np.float32).reshape(-1, 2)
        obj_points = np.asarray(obj_points, dtype=np.float32).reshape(-1, 2).copy()
        img_points = np.asarray(img_points, dtype=np.float32).reshape(-1, 2).copy()

        if obj_points.shape != img_points.shape:
            print(
                f"❌ Mismatch in point shapes: obj={obj_points.shape}, img={img_points.shape}"
            )
            return None

        if len(obj_points) < 3:
            print("❌ ERROR: At least 3 points are required for affine transformation.")
            return None

        # Check for duplicate points
        unique_obj = len(np.unique(obj_points, axis=0))
        unique_img = len(np.unique(img_points, axis=0))
        print(
            f"🔎 Unique object points: {unique_obj}, Unique image points: {unique_img}"
        )

        try:
            affine_matrix, _ = cv2.estimateAffinePartial2D(obj_points, img_points)
            if affine_matrix is None:
                raise ValueError("estimateAffinePartial2D returned None")
            print("✅ Affine matrix (partial) computed successfully.")
            return affine_matrix
        except Exception as e:
            print(f"⚠️ Partial affine estimation failed: {e}")
            print("🔁 Trying full affine estimation...")

            try:
                affine_matrix, _ = cv2.estimateAffine2D(obj_points, img_points)
                if affine_matrix is None:
                    print("❌ Full affine estimation also failed.")
                    return None
                print("✅ Affine matrix (full) computed as fallback.")
                return affine_matrix
            except Exception as ee:
                print(f"❌ Full affine estimation crashed: {ee}")
                return None

    def calibrate_camera(self):
        """Perform full 3D camera calibration and save results."""
        if not self.image_paths:
            QMessageBox.warning(
                self.view, "Error", "Please load images for calibration first."
            )
            return

        pattern_size = (
            self.view.grid_cols_input_1.value(),
            self.view.grid_rows_input_1.value(),
        )
        spacing = 1.0  # Use unit spacing; real-world scaling comes later

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
            pattern_type, obj_p, img_p = self.detect_pattern(img, pattern_size)
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
        print(f"Calibration RMS error: {ret:.4f}")
        if not ret:
            QMessageBox.warning(self.view, "Error", "Camera calibration failed.")
            return

        # Calculate 3D orientation
        rotation_matrix, tvec, euler_angles = self.calculate_3d_orientation(
            obj_points[0], img_points[0], mtx, dist
        )

        obj_pts_2d = obj_points[0][:, :2]  # shape (N, 2)
        img_pts_2d = img_points[0].reshape(-1, 2)  # shape (N, 2)

        if obj_pts_2d.shape == img_pts_2d.shape and len(obj_pts_2d) >= 3:
            affine_matrix = self.calculate_2d_affine_matrix(img, obj_pts_2d, img_pts_2d)
        else:
            print(
                f"⚠️ Skipping affine matrix — point mismatch or too few points: obj={obj_pts_2d.shape}, img={img_pts_2d.shape}"
            )
            affine_matrix = None

        # Step: build normalized square layout for the asymmetric pattern
        square_obj_pts = []
        for i in range(pattern_size[1]):  # rows
            for j in range(pattern_size[0]):  # cols
                x = 2 * j + (i % 2)
                y = i
                square_obj_pts.append([x, y])
        square_obj_pts = np.array(square_obj_pts, dtype=np.float32)
        square_obj_pts -= np.min(square_obj_pts, axis=0)
        scale = 1000.0 / np.max(square_obj_pts[:, 1])  # scale to 1000px height
        square_layout = square_obj_pts * scale

        H, _ = cv2.findHomography(img_pts_2d, square_layout)

        # Get ppm from stored value if available
        ppm_value = getattr(self, "ppm", None)

        # Store calibration data
        calibration_data = {
            "camera_matrix": mtx.tolist(),
            "dist_coeffs": dist.tolist(),
            "rvec": rvecs[0].tolist() if rvecs else None,
            "tvec": tvecs[0].tolist() if tvecs else None,
            "affine_matrix": (
                affine_matrix.tolist() if affine_matrix is not None else None
            ),
            "pixels_per_mm": ppm_value if ppm_value else None,
            "pattern_size": list(pattern_size),
            "centers": img_points[0].tolist(),  # shape (N, 1, 2)
            "square_layout": square_layout.tolist(),  # shape (N, 2)
            "homography": H.tolist(),
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
                "pixels_per_mm": calibration_data.get("pixels_per_mm", None),
                "pattern_size": tuple(calibration_data["pattern_size"]),
                "centers": np.array(calibration_data["centers"], dtype=np.float32),
                "square_layout": np.array(
                    calibration_data["square_layout"], dtype=np.float32
                ),
                "homography": np.array(
                    calibration_data["homography"], dtype=np.float32
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

    @staticmethod
    def apply_calibration(frame, calibration_data):
        """
        Apply calibration and homography using precomputed pattern points
        (no runtime detection).

        Args:
            frame (np.ndarray): Original image (BGR).
            calibration_data (dict): Must include:
                - 'camera_matrix': intrinsic matrix
                - 'dist_coeffs': distortion coefficients
                - 'centers': 2D detected points (Nx1x2)
                - 'square_layout': matching ideal square points (Nx2)
                - 'pattern_size': (cols, rows) of the asymmetric grid

        Returns:
            np.ndarray: Rectified image.
        """
        print("Calibration keys available:", list(calibration_data.keys()))
        camera_matrix = np.array(calibration_data["camera_matrix"], dtype=np.float32)
        dist_coeffs = np.array(calibration_data["dist_coeffs"], dtype=np.float32)
        centers = np.array(calibration_data["centers"], dtype=np.float32)
        square_layout = np.array(calibration_data["square_layout"], dtype=np.float32)

        h, w = frame.shape[:2]

        # Step 1: Undistort original image
        undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs)

        # Step 2: Compute homography from stored centers and layout
        H, _ = cv2.findHomography(centers, square_layout)

        # Step 3: Compute warped canvas bounds
        corners = np.array(
            [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32
        ).reshape(-1, 1, 2)
        warped_corners = cv2.perspectiveTransform(corners, H).reshape(-1, 2)
        min_x, min_y = np.min(warped_corners, axis=0)
        max_x, max_y = np.max(warped_corners, axis=0)

        # Step 4: Translate to avoid cropping
        T = np.array([[1, 0, -min_x], [0, 1, -min_y], [0, 0, 1]], dtype=np.float32)
        H_shifted = T @ H
        canvas_size = (int(np.ceil(max_x - min_x)), int(np.ceil(max_y - min_y)))

        # Step 5: Warp using final homography
        rectified = cv2.warpPerspective(undistorted, H_shifted, canvas_size)

        # ✅ Step 6: Rotate 90 degrees CCW to fix layout
        rectified_rotated = cv2.rotate(rectified, cv2.ROTATE_90_CLOCKWISE)

        return rectified_rotated
