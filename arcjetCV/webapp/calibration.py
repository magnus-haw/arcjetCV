"""
Headless calibration helpers for the web interface.

These mirror the desktop Calibration tab (``arcjetCV.calibration``): pattern
detection, camera calibration and rectification reuse the desktop code, but
every step reports errors by raising ``ValueError`` instead of opening Qt
dialogs, so they are safe to call from the Flask server.
"""

import json
import os
from pathlib import Path

import cv2 as cv
import numpy as np

IMAGE_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}

# Keys the desktop GUI reads from and writes to a calibration JSON file.
ARRAY_KEYS = [
    "camera_matrix",
    "dist_coeffs",
    "rvec",
    "tvec",
    "affine_matrix",
    "centers",
    "square_layout",
    "homography",
    "homography_inverse",
]

PATTERN_PDF = Path(__file__).resolve().parent.parent / "calibration" / "calibration.pdf"


def _controller():
    """A CalibrationController with no Qt view, used only for its pure helpers."""
    from arcjetCV.calibration.calibration_controller import CalibrationController

    return CalibrationController.__new__(CalibrationController)


def read_image(path, flags=cv.IMREAD_COLOR):
    if not os.path.isfile(path):
        raise ValueError(f"Image not found: {path}")
    img = cv.imread(path, flags)
    if img is None:
        raise ValueError(f"Could not read image: {os.path.basename(path)}")
    return img


def _pattern_size(cols, rows):
    cols, rows = int(cols), int(rows)
    if cols < 2 or rows < 2:
        raise ValueError("Pattern size must be at least 2 x 2.")
    return cols, rows


def calibrate_from_pattern(path, cols, rows):
    """
    Camera calibration from one pattern image.

    Same computation as ``CalibrationController.calibrate_camera``.
    """
    ctrl = _controller()
    pattern_size = _pattern_size(cols, rows)
    gray = read_image(path, cv.IMREAD_GRAYSCALE)

    pattern_type, obj_p, img_p = ctrl.detect_pattern(gray, pattern_size)
    if not pattern_type:
        raise ValueError(
            f'No pattern detected in "{os.path.basename(path)}". '
            "Check the pattern size (columns x rows)."
        )

    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(
        [obj_p], [img_p], gray.shape[::-1], None, None
    )
    if not ret:
        raise ValueError("Camera calibration failed.")

    obj_pts_2d = obj_p[:, :2]
    img_pts_2d = img_p.reshape(-1, 2)
    affine = None
    if obj_pts_2d.shape == img_pts_2d.shape and len(obj_pts_2d) >= 3:
        affine = ctrl.calculate_2d_affine_matrix(gray, obj_pts_2d, img_pts_2d)

    square_obj_pts = np.array(
        [
            [2 * j + (i % 2), i]
            for i in range(pattern_size[1])
            for j in range(pattern_size[0])
        ],
        dtype=np.float32,
    )
    square_obj_pts -= np.min(square_obj_pts, axis=0)
    square_layout = square_obj_pts * (1000.0 / np.max(square_obj_pts[:, 1]))

    H, _ = cv.findHomography(img_pts_2d, square_layout)
    if H is None:
        raise ValueError("Could not compute the pattern homography.")

    return {
        "camera_matrix": mtx.tolist(),
        "dist_coeffs": dist.tolist(),
        "rvec": rvecs[0].tolist() if rvecs else None,
        "tvec": tvecs[0].tolist() if tvecs else None,
        "affine_matrix": affine.tolist() if affine is not None else None,
        "pattern_size": list(pattern_size),
        "centers": img_p.tolist(),
        "square_layout": square_layout.tolist(),
        "homography": H.tolist(),
        "homography_inverse": np.linalg.inv(H).tolist(),
    }


def apply_calibration(frame, calibration):
    """Undistort and rectify a BGR frame, exactly like the desktop GUI."""
    from arcjetCV.calibration.calibration_controller import CalibrationController

    return CalibrationController.apply_calibration(frame, calibration)


def measure_pattern(path, cols, rows, diagonal_mm=None):
    """
    Desktop "Pattern Resolution" flow: calibrate, rectify, then measure the
    diagonal between the first and last detected pattern points.

    Returns (calibration dict, annotated RGB image, diagonal in px, pattern type).
    """
    calibration = calibrate_from_pattern(path, cols, rows)
    pattern_size = _pattern_size(cols, rows)

    image = apply_calibration(read_image(path), calibration)
    gray = cv.cvtColor(image, cv.COLOR_BGR2GRAY)
    pattern_type, _, corners = _controller().detect_pattern(gray, pattern_size)
    if pattern_type is None:
        raise ValueError("No valid pattern detected in the rectified image.")

    if pattern_type in {"chessboard", "circles_grid"}:
        cv.drawChessboardCorners(image, pattern_size, corners, True)

    p0 = np.asarray(corners[0][0], dtype=float)
    p1 = np.asarray(corners[-1][0], dtype=float)
    diagonal_px = float(np.linalg.norm(p0 - p1))

    thick = max(2, image.shape[1] // 400)
    a, b = tuple(int(round(v)) for v in p0), tuple(int(round(v)) for v in p1)
    cv.line(image, a, b, (0, 0, 255), thick)
    for pt in (a, b):
        cv.circle(image, pt, thick * 4, (0, 255, 255), -1)

    calibration["pixels_per_mm"] = None
    if diagonal_mm not in (None, ""):
        diagonal_mm = float(diagonal_mm)
        if diagonal_mm > 0:
            calibration["pixels_per_mm"] = diagonal_px / diagonal_mm

    rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
    return calibration, rgb, diagonal_px, pattern_type


def load_calibration(path):
    """Read a calibration JSON, keeping only the keys the desktop GUI uses."""
    try:
        with open(path, "r") as f:
            raw = json.load(f)
    except FileNotFoundError:
        raise ValueError(f"File not found: {path}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"Not a valid JSON file: {exc}")
    if not isinstance(raw, dict):
        raise ValueError("Calibration file must contain a JSON object.")

    data = {k: raw[k] for k in ARRAY_KEYS if raw.get(k) is not None}
    if "pattern_size" in raw:
        data["pattern_size"] = list(raw["pattern_size"])
    if raw.get("pixels_per_mm") not in (None, ""):
        data["pixels_per_mm"] = float(raw["pixels_per_mm"])
    if not data:
        raise ValueError(
            "No calibration fields found (expected pixels_per_mm or camera parameters)."
        )
    return data


def has_camera_model(calibration):
    return all(
        k in calibration
        for k in ("camera_matrix", "dist_coeffs", "centers", "square_layout")
    )


def save_calibration(path, calibration):
    """Write a calibration JSON in the same format as the desktop Save Calibration."""
    out = {k: calibration[k] for k in ARRAY_KEYS if k in calibration}
    if "pattern_size" in calibration:
        out["pattern_size"] = list(calibration["pattern_size"])
    if calibration.get("pixels_per_mm") not in (None, ""):
        out["pixels_per_mm"] = float(calibration["pixels_per_mm"])
    if not out:
        raise ValueError("No calibration data to save.")

    path = os.path.abspath(os.path.expanduser(path))
    if not path.lower().endswith(".json"):
        path += ".json"
    folder = os.path.dirname(path)
    if not os.path.isdir(folder):
        raise ValueError(f"Folder not found: {folder}")
    with open(path, "w") as f:
        json.dump(out, f, indent=4)
    return path
