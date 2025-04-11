import pytest
import os
import cv2
import json
import numpy as np
from unittest.mock import patch
from pathlib import Path
from PySide6.QtWidgets import QMessageBox, QApplication
from PySide6.QtTest import QTest
from PySide6.QtCore import Qt, QTimer
from arcjetCV.calibration.calibration_view import CalibrationView
from arcjetCV.calibration.calibration_controller import CalibrationController


@pytest.fixture(scope="session")
def app():
    """Ensure a single QApplication instance for the entire test session."""
    app = QApplication.instance() or QApplication([])
    yield app
    app.quit()


@pytest.fixture
def calibration_controller(qtbot):
    """Initialize the CalibrationController with a GUI view."""
    view = CalibrationView()
    qtbot.addWidget(view)
    controller = CalibrationController(view)
    return controller


@pytest.fixture
def test_images(tmp_path):
    """Generate synthetic chessboard images for testing."""
    output_dir = tmp_path / "test_images"
    output_dir.mkdir()

    grid_size = (9, 6)
    square_size = 50

    image_paths = []
    for i in range(3):  # Generate 3 images for faster testing
        img = (
            np.ones(
                (grid_size[1] * square_size, grid_size[0] * square_size, 3),
                dtype=np.uint8,
            )
            * 255
        )

        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                if (x + y) % 2 == 0:
                    cv2.rectangle(
                        img,
                        (x * square_size, y * square_size),
                        ((x + 1) * square_size, (y + 1) * square_size),
                        (0, 0, 0),
                        -1,
                    )

        image_path = output_dir / f"chessboard_{i + 1}.png"
        cv2.imwrite(str(image_path), img)
        image_paths.append(str(image_path))

    return image_paths


def auto_dismiss_popup():
    """Automatically close QMessageBox after a short delay."""

    def close_popup():
        for widget in QApplication.topLevelWidgets():
            if isinstance(widget, QMessageBox):
                widget.done(QMessageBox.Ok)

    QTimer.singleShot(1000, close_popup)  # Auto-close after 1 second


def find_project_root():
    """Find the root directory of the project."""
    current_path = Path(__file__).resolve().parent
    while current_path != current_path.root:
        if (current_path / "setup.py").exists() or (
            current_path / "pyproject.toml"
        ).exists():
            return current_path
        current_path = current_path.parent
    return Path(__file__).resolve().parent


def get_calibration_image():
    """Load a specific calibration pattern image for testing."""
    project_root = find_project_root()
    image_path = project_root / "tests" / "arcjetcv_calibration.jpg"

    assert image_path.exists(), f"Test image not found: {image_path}"
    img = cv2.imread(str(image_path))
    assert img is not None, "Failed to load calibration image."
    return img


def test_detect_pattern(calibration_controller, qtbot):
    """Test pattern detection from the calibration image with popup handling."""
    controller = calibration_controller
    img = get_calibration_image()

    # Convert to grayscale if the image is in color
    if len(img.shape) == 3 and img.shape[2] == 3:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Auto-dismiss any popup during pattern detection
    auto_dismiss_popup()

    pattern_type, obj_points, img_points = controller.detect_pattern(img, (4, 9))

    assert pattern_type == "asymmetric_circles_grid", "Pattern detection failed."
    assert obj_points is not None, "Object points not generated."
    assert img_points is not None, "Image points not generated."


# def test_calibrate_camera(calibration_controller, qtbot):
#     """Test the full camera calibration process using the calibration image."""
#     controller = calibration_controller
#     project_root = find_project_root()
#     image_path = project_root / "tests" / "arcjetcv_calibration.jpg"
#     controller.image_paths = [str(image_path)]

#     assert len(controller.image_paths) > 0, "No test images loaded for calibration."

#     # Auto-dismiss any popup during calibration
#     auto_dismiss_popup()

#     try:
#         controller.calibrate_camera()

#         # Ensure calibration data exists
#         assert controller.calibration_data, "Calibration data not stored."
#         assert "camera_matrix" in controller.calibration_data, "Camera matrix missing."
#         assert (
#             "dist_coeffs" in controller.calibration_data
#         ), "Distortion coefficients missing."

#         print("✅ Camera calibration completed successfully!")
#     except Exception as e:
#         pytest.fail(f"❌ Calibration raised an exception: {e}")


def test_apply_calibration(calibration_controller):
    """Test applying calibration to the calibration image."""
    controller = calibration_controller
    project_root = find_project_root()
    image_path = project_root / "tests" / "arcjetcv_calibration.jpg"

    # Set the expected pattern size (same as used during calibration)
    controller.view.grid_cols_input.setValue(4)
    controller.view.grid_rows_input.setValue(9)

    # Prevent popups from blocking the test
    with patch.object(QMessageBox, "information") as mock_info, patch.object(
        QMessageBox, "warning"
    ) as mock_warning:

        # Call the calibration function with correct signature
        controller.calibrate_camera(str(image_path))

        # Make sure calibration succeeded
        assert controller.calibration_data, "Calibration data not stored."

        # Check some essential fields
        assert "camera_matrix" in controller.calibration_data
        assert "dist_coeffs" in controller.calibration_data
        assert controller.calibrated is True

        # Load original image and apply calibration
        test_img = get_calibration_image()
        calibrated_img = controller.apply_calibration(
            test_img, controller.calibration_data
        )

        assert calibrated_img is not None, "Failed to apply calibration."
        assert calibrated_img.shape[2] == test_img.shape[2], "Channel count mismatch"
        assert (
            calibrated_img.shape[0] > 0 and calibrated_img.shape[1] > 0
        ), "Image shape invalid"

        # Confirm that a success popup was triggered
        mock_info.assert_called_once()


def test_save_to_json(calibration_controller, tmp_path):
    """Test saving calibration results to JSON."""
    controller = calibration_controller
    test_data = {
        "camera_matrix": [[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        "dist_coeffs": [0.1, 0.2, 0.3, 0.4, 0.5],
    }

    output_file = tmp_path / "calibration_test.json"
    success, error = controller.save_to_json(test_data, str(output_file))

    assert success, f"Failed to save JSON: {error}"
    assert output_file.exists(), "Output JSON file not created."

    with open(output_file, "r") as json_file:
        loaded_data = json.load(json_file)

    assert loaded_data["camera_matrix"] == test_data["camera_matrix"]
    assert loaded_data["dist_coeffs"] == test_data["dist_coeffs"]


def test_calculate_3d_orientation(calibration_controller):
    """Test calculation of 3D orientation."""
    controller = calibration_controller
    obj_points = np.array(
        [[0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]], dtype=np.float32
    )
    img_points = np.array(
        [[100, 100], [200, 100], [200, 200], [100, 200]], dtype=np.float32
    )

    camera_matrix = np.eye(3, dtype=np.float32)
    dist_coeffs = np.zeros(5, dtype=np.float32)

    # Auto-dismiss any popup during 3D orientation calculation
    auto_dismiss_popup()

    rotation_matrix, tvec, euler_angles = controller.calculate_3d_orientation(
        obj_points, img_points, camera_matrix, dist_coeffs
    )

    assert rotation_matrix is not None, "Failed to compute rotation matrix."
    assert tvec is not None, "Failed to compute translation vector."
    assert euler_angles is not None, "Failed to compute Euler angles."


def test_apply_calibration(calibration_controller):
    """Test applying calibration to the calibration image."""
    controller = calibration_controller
    project_root = find_project_root()
    image_path = project_root / "tests" / "arcjetcv_calibration.jpg"
    controller.image_paths = [str(image_path)]

    # Auto-dismiss any popup during calibration
    auto_dismiss_popup()

    controller.calibrate_camera(str(image_path))

    # Ensure calibration data exists
    assert controller.calibration_data, "Calibration data not stored."

    test_img = get_calibration_image()
    calibrated_img = controller.apply_calibration(test_img, controller.calibration_data)

    assert calibrated_img is not None, "Failed to apply calibration."

    # ✅ Allow different shape if homography changes canvas size
    assert (
        calibrated_img.shape[2] == test_img.shape[2]
    ), "Calibrated image channel mismatch"
    assert (
        calibrated_img.shape[0] > 0 and calibrated_img.shape[1] > 0
    ), "Calibrated image has invalid dimensions"
