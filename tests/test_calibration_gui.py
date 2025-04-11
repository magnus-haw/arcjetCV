import pytest
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from arcjetCV.calibration.calibration_view import CalibrationView


@pytest.fixture(scope="module")
def app():
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app
    app.quit()


@pytest.fixture
def view(app):
    return CalibrationView()


def test_calibration_view_initialization(view):
    """Test that the CalibrationView initializes correctly."""
    assert view is not None
    assert view.print_button.text() == "Print Chessboard"
    assert view.grid_rows_input.value() == 9
    assert view.grid_cols_input.value() == 4
    assert view.ppcm_label.text() == "Calibration Scale: N/A"


def test_grid_size_spinboxes(view):
    """Test the grid size spinboxes for pattern resolution."""
    view.grid_rows_input.setValue(12)
    view.grid_cols_input.setValue(8)

    assert view.grid_rows_input.value() == 12
    assert view.grid_cols_input.value() == 8


def test_button_clicks(view, qtbot):
    """Test main buttons are clickable and exist."""
    # Print button
    qtbot.mouseClick(view.print_button, Qt.LeftButton)
    assert view.print_button.isEnabled()

    # Load calibration image (pattern resolution tab)
    qtbot.mouseClick(view.load_image_button_pattern, Qt.LeftButton)
    assert view.load_image_button_pattern.isEnabled()

    # Load image for ruler resolution tab
    qtbot.mouseClick(view.load_image_button, Qt.LeftButton)
    assert view.load_image_button.isEnabled()

    # Save calibration button
    qtbot.mouseClick(view.save_calibration_button, Qt.LeftButton)
    assert view.save_calibration_button.isEnabled()


def test_diagonal_input(view):
    """Test the diagonal distance input widget."""
    view.diagonal_distance_value.setValue(150.0)
    assert view.diagonal_distance_value.value() == 150.0


def test_real_world_length_input(view):
    """Test the ruler-based real-world length input."""
    test_value = "123.45"
    view.distance_input.setText(test_value)
    assert view.distance_input.text() == test_value
