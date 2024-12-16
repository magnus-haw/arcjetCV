import cv2
import json
import numpy as np


class CalibrationModel:
    def __init__(self):
        self.camera_matrix = None
        self.dist_coeffs = None
        self.rotation_vectors = None
        self.translation_vectors = None

    def calibrate_camera(self, image_paths, chessboard_size, square_size):
        """Perform camera calibration."""
        objp = np.zeros((chessboard_size[0] * chessboard_size[1], 3), np.float32)
        objp[:, :2] = np.mgrid[
            0 : chessboard_size[0], 0 : chessboard_size[1]
        ].T.reshape(-1, 2)
        objp *= square_size

        objpoints = []
        imgpoints = []

        for path in image_paths:
            image = cv2.imread(path)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)
            if ret:
                objpoints.append(objp)
                imgpoints.append(corners)

        if not objpoints or not imgpoints:
            return False, "No chessboard corners detected"

        (
            ret,
            self.camera_matrix,
            self.dist_coeffs,
            self.rotation_vectors,
            self.translation_vectors,
        ) = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
        return ret, None

    def save_calibration(self, filename="calibration.json"):
        """Save calibration results to a file."""
        if not self.camera_matrix:
            return False, "No calibration data available"
        data = {
            "camera_matrix": self.camera_matrix.tolist(),
            "distortion_coefficients": self.dist_coeffs.tolist(),
            "rotation_vectors": [rv.tolist() for rv in self.rotation_vectors],
            "translation_vectors": [tv.tolist() for tv in self.translation_vectors],
        }
        try:
            with open(filename, "w") as file:
                json.dump(data, file, indent=4)
            return True, None
        except Exception as e:
            return False, str(e)
