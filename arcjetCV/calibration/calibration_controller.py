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

        # # Connect signals and slots
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

    def _generate_object_points(self, pattern_size, pattern_type, spacing=1.0):
        """
        Generate 3D object points based on the calibration pattern type and spacing.

        This function produces the object points assuming the pattern lies on the Z=0 plane.
        For asymmetric circle grids, the layout accounts for offset rows.

        :param pattern_size: Tuple[int, int]
            Size of the pattern (columns, rows).
        :param pattern_type: str
            One of "chessboard", "circles_grid", or "asymmetric_circles_grid".
        :param spacing: float, optional
            Real-world spacing between adjacent points, in user-defined units (default is 1.0).

        :return: np.ndarray
            A NumPy array of shape (N, 3) or (N, 1, 3) with 3D object points.
        """
        cols, rows = pattern_size

        if pattern_type in {"chessboard", "circles_grid"}:
            obj_points = np.zeros((rows * cols, 3), dtype=np.float32)
            obj_points[:, :2] = np.mgrid[0:cols, 0:rows].T.reshape(-1, 2)
            obj_points *= spacing
            return obj_points

        elif pattern_type == "asymmetric_circles_grid":
            obj_points = [
                [(2 * j + (i % 2)) * spacing / 2.0, i * spacing, 0]
                for i in range(rows)
                for j in range(cols)
            ]
            return np.array(obj_points, dtype=np.float32).reshape(-1, 1, 3)

        raise ValueError(f"Unsupported pattern_type: '{pattern_type}'")

    def detect_pattern(self, img, pattern_size):
        """
        Detect the type of calibration pattern in a grayscale image.

        This method attempts to detect one of the following pattern types in the given image:
        - Chessboard
        - Symmetric circle grid
        - Asymmetric circle grid
        - Custom asymmetric pattern using blob detection (as fallback)

        :param img: Grayscale image in which to detect the pattern.
        :type img: numpy.ndarray
        :param pattern_size: Size of the pattern as (columns, rows).
        :type pattern_size: tuple[int, int]

        :return: A tuple containing:
            - str: Detected pattern type ("chessboard", "circles_grid", "asymmetric_circles_grid") or None.
            - numpy.ndarray: 3D object points corresponding to the detected pattern.
            - numpy.ndarray: 2D image points found in the image.
        :rtype: tuple[str, numpy.ndarray, numpy.ndarray]
        """
        # Enhance contrast for better detection
        img = cv2.equalizeHist(img)

        # Try detecting a chessboard pattern
        found, corners = cv2.findChessboardCorners(img, pattern_size)
        if found:
            return (
                "chessboard",
                self._generate_object_points(pattern_size, "chessboard"),
                corners,
            )

        # Try detecting a symmetric circles grid
        found, centers = cv2.findCirclesGrid(
            img, pattern_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID
        )
        if found:
            return (
                "circles_grid",
                self._generate_object_points(pattern_size, "circles_grid"),
                centers,
            )

        # Try detecting an asymmetric circles grid
        found, centers = cv2.findCirclesGrid(
            img, pattern_size, flags=cv2.CALIB_CB_ASYMMETRIC_GRID
        )
        if found:
            return (
                "asymmetric_circles_grid",
                self._generate_object_points(pattern_size, "asymmetric_circles_grid"),
                centers,
            )

        # Custom asymmetric pattern detection (2 attempts with different parameters)
        for min_area, max_area in [(3000, 15000), (500, 3000)]:
            result = self.found_asym_pattern(img, pattern_size, min_area, max_area)
            if result[0] is not None:
                return result

        # No pattern found
        return None, None, None

    def asym_obj_points(self, rows, cols):
        """
        Generate 3D object points for an asymmetric circle grid pattern.

        This layout offsets every other column by 0.5 units horizontally,
        mimicking the staggered dot pattern used in asymmetric calibration targets.
        The points lie in the Z=0 plane.

        :param rows: Number of rows in the pattern.
        :type rows: int
        :param cols: Number of columns in the pattern.
        :type cols: int

        :return: Object points array of shape (rows * cols, 3), where each point is [x, y, 0].
        :rtype: numpy.ndarray
        """
        points = np.zeros((rows * cols, 3), dtype=np.float32)
        points[:, :2] = np.mgrid[0:rows, 0:cols].T.reshape(-1, 2)

        # Apply horizontal offset to every other column
        for col in range(1, cols, 2):
            indices = col * rows + np.arange(rows)
            points[indices, 0] += 0.5

        return points

    def found_asym_pattern(self, img, pattern_size, minArea, maxArea):
        """
        Custom asymmetric circle grid detection using a blob detector.

        This method acts as a fallback when OpenCV's `cv2.findCirclesGrid` fails
        to detect an asymmetric pattern. It enhances the image and applies blob
        detection to locate the circular pattern, and then refines the corners.

        :param img: Grayscale input image.
        :type img: numpy.ndarray
        :param pattern_size: Tuple of (columns, rows) representing the dot grid size.
        :type pattern_size: tuple
        :param minArea: Minimum area of a blob to be considered valid.
        :type minArea: float
        :param maxArea: Maximum area of a blob to be considered valid.
        :type maxArea: float

        :return: A tuple containing:
                - Detected pattern type as a string.
                - 3D object points as a NumPy array.
                - 2D image points as a NumPy array.
                If detection fails, all returned values are None.
        :rtype: tuple[str, numpy.ndarray, numpy.ndarray] | tuple[None, None, None]
        """
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

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

        objp = self.asym_obj_points(pattern_size[1], pattern_size[0])

        blurred = cv2.GaussianBlur(img, (15, 15), 0)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        clahe_img = clahe.apply(blurred)
        sharpened = cv2.filter2D(
            clahe_img, -1, np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
        )

        keypoints = blobDetector.detect(sharpened)
        if not keypoints:
            print("❌ No keypoints found, asymmetric grid detection failed.")
            return None, None, None

        im_with_keypoints = cv2.drawKeypoints(
            img,
            keypoints,
            np.array([]),
            (0, 255, 0),
            cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
        )
        im_with_keypoints_gray = cv2.cvtColor(im_with_keypoints, cv2.COLOR_BGR2GRAY)

        ret, corners = cv2.findCirclesGrid(
            img,
            pattern_size,
            flags=(cv2.CALIB_CB_ASYMMETRIC_GRID + cv2.CALIB_CB_CLUSTERING),
            blobDetector=blobDetector,
        )

        if not ret:
            print("❌ Custom asymmetric detection failed.")
            return None, None, None

        corners2 = cv2.cornerSubPix(
            im_with_keypoints_gray, corners, (11, 11), (-1, -1), criteria
        )
        return "asymmetric_circles_grid", objp, corners2

    def save_to_json(self, calibration_data, file_path="calibration_results.json"):
        """
        Save calibration parameters to a JSON file.

        This function merges the given calibration data with any existing file,
        and writes the combined result back to disk.

        :param calibration_data: Dictionary containing calibration parameters to save.
        :type calibration_data: dict
        :param file_path: Relative or absolute path to the JSON file.
        :type file_path: str

        :return: Tuple indicating success and an optional error message.
        :rtype: tuple[bool, str or None]
        """
        try:
            script_directory = os.path.dirname(os.path.abspath(__file__))
            file_path = os.path.join(script_directory, file_path)

            with open(file_path, "w") as json_file:
                json.dump(calibration_data, json_file, indent=4)

            print(str(file_path))
            return True, None
        except Exception as e:
            return False, str(e)

    def calculate_3d_orientation(
        self, obj_points, img_points, camera_matrix, dist_coeffs
    ):
        """
        Calculate 3D orientation using PnP pose estimation.

        Converts object and image points into a rotation matrix and translation vector,
        then converts the rotation into Euler angles.

        :param obj_points: List of 3D object points.
        :type obj_points: list or numpy.ndarray
        :param img_points: List of corresponding 2D image points.
        :type img_points: list or numpy.ndarray
        :param camera_matrix: Camera intrinsic matrix.
        :type camera_matrix: numpy.ndarray
        :param dist_coeffs: Distortion coefficients.
        :type dist_coeffs: numpy.ndarray

        :return: Tuple of (rotation matrix, translation vector, Euler angles in degrees).
        :rtype: tuple[numpy.ndarray, numpy.ndarray, tuple[float, float, float]]
        """
        ret, rvec, tvec = cv2.solvePnP(
            obj_points, img_points, camera_matrix, dist_coeffs
        )
        if not ret:
            QMessageBox.warning(self.view, "Error", "3D Pose estimation failed.")
            return None

        rotation_matrix, _ = cv2.Rodrigues(rvec)

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
        Estimate a 2D affine transformation matrix between object and image points.

        This method first attempts a partial affine transformation, and falls back
        to a full affine transformation if necessary.

        :param img: The image on which points were detected.
        :type img: numpy.ndarray
        :param obj_points: 2D object points in the reference space.
        :type obj_points: numpy.ndarray
        :param img_points: 2D points detected in the image.
        :type img_points: numpy.ndarray

        :return: 2D affine transformation matrix or None if estimation fails.
        :rtype: numpy.ndarray or None
        """
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

        print(
            f"🔎 Unique object points: {len(np.unique(obj_points, axis=0))}, "
            f"Unique image points: {len(np.unique(img_points, axis=0))}"
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

    def calibrate_camera(self, img_path):
        """
        Perform full 3D camera calibration and save results to JSON.

        This method:
        - Detects a calibration pattern in the given image.
        - Computes intrinsic and extrinsic camera parameters.
        - Estimates an affine and homography transformation.
        - Stores all calibration outputs in a JSON file.

        :param img_path: Path to the grayscale image containing the calibration pattern.
        :type img_path: str

        :return: None. Results are stored in self.calibration_data and JSON.
        :rtype: None
        """
        pattern_size = (
            self.view.grid_cols_input.value(),
            self.view.grid_rows_input.value(),
        )
        spacing = 1.0

        obj_points = []
        img_points = []

        img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
        if img is None:
            QMessageBox.warning(self.view, "Error", f"Failed to load image: {img_path}")
            return

        pattern_type, obj_p, img_p = self.detect_pattern(img, pattern_size)
        if pattern_type:
            obj_points.append(obj_p)
            img_points.append(img_p)
        else:
            QMessageBox.warning(
                self.view, "Error", f"No pattern detected in {img_path}"
            )
            return

        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points, img_points, img.shape[::-1], None, None
        )
        print(f"Calibration RMS error: {ret:.4f}")
        if not ret:
            QMessageBox.warning(self.view, "Error", "Camera calibration failed.")
            return

        rotation_matrix, tvec, euler_angles = self.calculate_3d_orientation(
            obj_points[0], img_points[0], mtx, dist
        )

        obj_pts_2d = obj_points[0][:, :2]
        img_pts_2d = img_points[0].reshape(-1, 2)

        if obj_pts_2d.shape == img_pts_2d.shape and len(obj_pts_2d) >= 3:
            affine_matrix = self.calculate_2d_affine_matrix(img, obj_pts_2d, img_pts_2d)
        else:
            print("⚠️ Skipping affine matrix due to mismatch or insufficient points")
            affine_matrix = None

        square_obj_pts = []
        for i in range(pattern_size[1]):
            for j in range(pattern_size[0]):
                x = 2 * j + (i % 2)
                y = i
                square_obj_pts.append([x, y])
        square_obj_pts = np.array(square_obj_pts, dtype=np.float32)
        square_obj_pts -= np.min(square_obj_pts, axis=0)
        scale = 1000.0 / np.max(square_obj_pts[:, 1])
        square_layout = square_obj_pts * scale

        H, _ = cv2.findHomography(img_pts_2d, square_layout)
        H_inv = np.linalg.inv(H)
        ppm_value = getattr(self, "ppm", None)

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
            "centers": img_points[0].tolist(),
            "square_layout": square_layout.tolist(),
            "homography": H.tolist(),
            "homography_inverse": H_inv.tolist(),
        }

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
                "homography_inverse": np.array(
                    calibration_data["homography_inverse"], dtype=np.float32
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
        """
        Generate and print a chessboard calibration pattern.

        Creates a standard black-and-white chessboard PNG image and attempts to print it.
        The generated file is saved as 'chessboard_pattern.png' and printed via QPrinter.

        :return: None
        :rtype: None
        """
        filename = "chessboard_pattern.png"
        rows, cols, square_size = 9, 6, 50
        image_size = (cols * square_size, rows * square_size)

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
        """
        Display the loaded image and enable interactive line drawing.

        This method sets up the matplotlib canvas to allow the user to draw a line
        by clicking and dragging. Useful for manual resolution calibration.
        """
        self.view.figure.clear()
        self.ax = self.view.figure.add_subplot(111)
        self.ax.imshow(self.image)
        self.ax.set_title("Click and drag to draw a line")
        self.ax.figure.canvas.set_cursor(cursors.SELECT_REGION)
        self.view.canvas.draw()

        self.line_artist = None

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
        """
        Record the starting point of a line when mouse button is pressed.

        :param event: Mouse press event.
        :type event: matplotlib.backend_bases.MouseEvent
        """
        if event.inaxes != self.ax:
            return
        self.start_point = (event.xdata, event.ydata)

        if self.line_artist:
            self.line_artist.remove()
            self.line_artist = None
        self.view.canvas.draw()

    def on_mouse_motion(self, event):
        """
        Update the line dynamically as the mouse moves.

        :param event: Mouse move event.
        :type event: matplotlib.backend_bases.MouseEvent
        """
        if event.inaxes != self.ax or not self.start_point:
            return

        if self.line_artist:
            self.line_artist.remove()

        end_point = (event.xdata, event.ydata)
        (self.line_artist,) = self.ax.plot(
            [self.start_point[0], end_point[0]],
            [self.start_point[1], end_point[1]],
            color="red",
            linewidth=2,
        )
        self.view.canvas.draw()

    def on_mouse_release(self, event):
        """
        Finalize the line when the mouse button is released.

        :param event: Mouse release event.
        :type event: matplotlib.backend_bases.MouseEvent
        """
        if event.inaxes != self.ax or not self.start_point:
            return

        end_point = (event.xdata, event.ydata)
        self.line = (self.start_point, end_point)

        if self.line_artist:
            self.line_artist.remove()
        (self.line_artist,) = self.ax.plot(
            [self.start_point[0], end_point[0]],
            [self.start_point[1], end_point[1]],
            color="red",
            linewidth=2,
        )

        self.view.canvas.draw()
        self.start_point = None

    def load_image_diagonal(self):
        """
        Load an image, perform pattern detection, and draw the diagonal across detected pattern.

        This function performs a calibration and rectification step before detecting the pattern.
        It displays the diagonal length on the GUI after drawing it over the image.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self.view,
            "Load Image for Pattern Detection",
            "",
            "Images (*.png *.jpg *.jpeg)",
        )
        if not file_path:
            QMessageBox.warning(self.view, "Error", "No image selected.")
            return

        self.image = cv2.imread(file_path)
        self.calibrate_camera(file_path)
        self.image = self.apply_calibration(self.image, self.calibration_data)

        if self.image is None:
            QMessageBox.warning(self.view, "Error", "Unable to load the image.")
            return

        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        pattern_size = (
            self.view.grid_cols_input.value(),
            self.view.grid_rows_input.value(),
        )

        pattern_type, obj_points, corners = self.detect_pattern(gray, pattern_size)
        if pattern_type is None:
            QMessageBox.warning(self.view, "Error", "No valid pattern detected.")
            return

        if pattern_type in {"chessboard", "circles_grid"}:
            cv2.drawChessboardCorners(self.image, pattern_size, corners, True)

        top_left = corners[0][0]
        bottom_right = corners[-1][0]

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

        self.diagonal_distance = np.linalg.norm(top_left - bottom_right)
        QMessageBox.information(
            self.view,
            "Diagonal Length",
            f"Diagonal Distance: {self.diagonal_distance:.2f} pixels",
        )

    def calculate_ppcm(self):
        """
        Calculate pixels per mm using either diagonal or ruler mode.

        The function checks the current selected tab:
        - Pattern Mode: Uses automatically detected diagonal.
        - Ruler Mode: Uses a manually drawn line and user-specified length.
        """
        if self.image is None:
            QMessageBox.warning(self.view, "Error", "Please load an image first.")
            return

        current_tab_index = self.view.resolution_tabs.currentIndex()

        if current_tab_index == 0:
            try:
                real_length = self.view.diagonal_distance_value.value()
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
        elif current_tab_index == 1:
            if not self.line:
                QMessageBox.warning(
                    self.view, "Error", "Please draw a line on the image."
                )
                return
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

        self.save_ppm_to_json()

    def save_ppm_to_json(
        self,
        file_path=os.path.join(
            Path(__file__).parent.absolute(), "calibration_results.json"
        ),
    ):
        """
        Save the pixels-per-mm (ppm) value to a calibration JSON file.

        :param file_path: Destination path for the JSON file.
        :type file_path: str
        """
        if not hasattr(self, "ppm") or self.ppm is None:
            QMessageBox.warning(self.view, "Error", "No valid ppm value to save.")
            return

        try:
            ppm_value = float(self.ppm)
            if os.path.exists(file_path):
                with open(file_path, "r") as json_file:
                    try:
                        existing_data = json.load(json_file)
                    except json.JSONDecodeError:
                        existing_data = {}
            else:
                existing_data = {}

            existing_data["pixels_per_mm"] = ppm_value

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
        """
        Prompt the user to save the current calibration results as a JSON file.

        This method opens a file dialog, allows the user to choose a save path,
        copies the existing `calibration_results.json` to that location,
        and resets the original file to an empty structure.

        If the save fails, an error message is shown.

        :raises QMessageBox.critical: If copying or saving fails.
        """
        default_filename = "calibration_copy.json"

        file_path, _ = QFileDialog.getSaveFileName(
            None, "Save Calibration", "", "JSON Files (*.json);;All Files (*)"
        )

        if file_path:
            source_file = os.path.join(
                Path(__file__).parent.absolute(), "calibration_results.json"
            )
            try:
                shutil.copy(source_file, file_path)
                with open(source_file, "w") as f:
                    f.write("{}")
                QMessageBox.information(
                    self.view, "Success", f"Calibration saved as {file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self.view, "Error", f"Failed to save calibration: {e}"
                )

    @staticmethod
    def apply_calibration(frame, calibration_data):
        """
        Apply distortion correction and perspective homography to an image using stored calibration data.

        If only 'pixels_per_mm' is provided, returns the original image without transformation.

        :param frame: The original distorted image (in BGR format).
        :type frame: np.ndarray
        :param calibration_data: Dictionary containing calibration results. Can include:
            - 'camera_matrix': Intrinsic camera matrix (3x3).
            - 'dist_coeffs': Distortion coefficients (1x5 or 1x8).
            - 'centers': 2D detected pattern points (Nx1x2).
            - 'square_layout': Ideal layout corresponding to detected points (Nx2).
            - 'pattern_size': Pattern dimensions (cols, rows).
            - 'pixels_per_mm': Optional scale for mm/pixel resolution.
        :type calibration_data: dict

        :return: The rectified image (undistorted and warped to a square-aligned frame), or original if not applicable.
        :rtype: np.ndarray
        """
        print("Calibration keys available:", list(calibration_data.keys()))

        if all(
            k in calibration_data
            for k in ["camera_matrix", "dist_coeffs", "centers", "square_layout"]
        ):
            camera_matrix = np.array(
                calibration_data["camera_matrix"], dtype=np.float32
            )
            dist_coeffs = np.array(calibration_data["dist_coeffs"], dtype=np.float32)
            centers = np.array(calibration_data["centers"], dtype=np.float32)
            square_layout = np.array(
                calibration_data["square_layout"], dtype=np.float32
            )

            h, w = frame.shape[:2]
            undistorted = cv2.undistort(frame, camera_matrix, dist_coeffs)
            H, _ = cv2.findHomography(centers, square_layout)

            corners = np.array(
                [[0, 0], [w - 1, 0], [w - 1, h - 1], [0, h - 1]], dtype=np.float32
            ).reshape(-1, 1, 2)
            warped_corners = cv2.perspectiveTransform(corners, H).reshape(-1, 2)
            min_x, min_y = np.min(warped_corners, axis=0)
            max_x, max_y = np.max(warped_corners, axis=0)

            T = np.array([[1, 0, -min_x], [0, 1, -min_y], [0, 0, 1]], dtype=np.float32)
            H_shifted = T @ H
            canvas_size = (int(np.ceil(max_x - min_x)), int(np.ceil(max_y - min_y)))
            rectified = cv2.warpPerspective(undistorted, H_shifted, canvas_size)
            return cv2.rotate(rectified, cv2.ROTATE_90_CLOCKWISE)

        elif "pixels_per_mm" in calibration_data:
            print(
                "⚠️ Only pixels_per_mm provided. No distortion or rectification applied."
            )
            return frame

        else:
            print("⚠️ No usable calibration data found. Returning original frame.")
            return frame
