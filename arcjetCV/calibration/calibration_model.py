import cv2
import json
import numpy as np
import os
from PySide6.QtWidgets import QMessageBox


class CalibrationModel:
    def __init__(self):
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rotation_vectors = None
        self.translation_vectors = None

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

            return True, None
        except Exception as e:
            return False, str(e)

    @staticmethod
    def detect_pattern(img, chessboard_size, circles_grid_size):
        """
        Detect whether the image contains a chessboard or a circles grid.

        Args:
            img (numpy.ndarray): The grayscale image to analyze.
            chessboard_size (tuple): Chessboard pattern size (columns, rows).
            circles_grid_size (tuple): Circles grid pattern size (columns, rows).

        Returns:
            tuple: (str, object_points, image_points)
                str: "chessboard", "circles_grid", or None.
                object_points: 3D points in real-world space.
                image_points: 2D points in the image plane.
        """
        # Prepare 3D object points for chessboard and circles grid
        chessboard_obj_points = np.zeros(
            (chessboard_size[0] * chessboard_size[1], 3), np.float32
        )
        chessboard_obj_points[:, :2] = np.mgrid[
            0 : chessboard_size[0], 0 : chessboard_size[1]
        ].T.reshape(-1, 2)

        circles_obj_points = np.zeros(
            (circles_grid_size[0] * circles_grid_size[1], 3), np.float32
        )
        circles_obj_points[:, :2] = np.mgrid[
            0 : circles_grid_size[0], 0 : circles_grid_size[1]
        ].T.reshape(-1, 2)

        # Try detecting chessboard pattern
        ret_chessboard, corners_chessboard = cv2.findChessboardCorners(
            img, chessboard_size
        )
        if ret_chessboard:
            return "chessboard", chessboard_obj_points, corners_chessboard

        # Try detecting circles grid pattern
        ret_circles_grid, centers_circles_grid = cv2.findCirclesGrid(
            img, circles_grid_size, flags=cv2.CALIB_CB_SYMMETRIC_GRID
        )
        if ret_circles_grid:
            return "circles_grid", circles_obj_points, centers_circles_grid

        # No pattern detected
        return None, None, None

    def calibrate_camera(self):
        """Automatically detect pattern type, perform camera calibration, and save to a JSON file."""
        if not hasattr(self, "image_paths") or not self.image_paths:
            QMessageBox.warning(
                self.view, "Error", "Please load images for calibration first."
            )
            return

        chessboard_size = (9, 6)  # Inner corners for chessboard
        circles_grid_size = (4, 11)  # Circle pattern grid size
        square_size = 1.0  # Real-world square/circle size

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
                img, chessboard_size, circles_grid_size
            )
            if pattern_type:
                obj_points.append(obj_p)
                img_points.append(img_p)
            else:
                QMessageBox.warning(
                    self.view, "Error", f"No pattern detected in image: {img_path}"
                )
                return

        # Perform calibration
        ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(
            obj_points, img_points, img.shape[::-1], None, None
        )

        if not ret:
            QMessageBox.warning(self.view, "Error", "Camera calibration failed.")
            return

        # Compute orientation (rotation matrices and Euler angles)
        orientation_matrices = []
        euler_angles = []

        for rvec in rvecs:
            # Convert rotation vector to rotation matrix
            rotation_matrix, _ = cv2.Rodrigues(rvec)
            orientation_matrices.append(rotation_matrix.tolist())

            # Convert rotation matrix to Euler angles
            sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
            singular = sy < 1e-6
            if not singular:
                x = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
                y = np.arctan2(-rotation_matrix[2, 0], sy)
                z = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
            else:
                x = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
                y = np.arctan2(-rotation_matrix[2, 0], sy)
                z = 0
            euler_angles.append([np.degrees(angle) for angle in (x, y, z)])

        # Save calibration results
        calibration_data = {
            "camera_matrix": mtx.tolist(),
            "dist_coeffs": dist.tolist(),
            "rotation_vectors": [vec.tolist() for vec in rvecs],
            "translation_vectors": [vec.tolist() for vec in tvecs],
            "orientation_matrices": orientation_matrices,
            "euler_angles": euler_angles,
        }

        success, save_error = self.save_to_json(calibration_data)
        if success:
            QMessageBox.information(
                self.view, "Success", "Camera calibration successful and saved."
            )
        else:
            QMessageBox.warning(
                self.view, "Error", f"Failed to save calibration: {save_error}"
            )
