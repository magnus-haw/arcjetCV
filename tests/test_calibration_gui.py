import pytest
from PySide6.QtWidgets import QApplication
from arcjetCV.calibration.calibration_view import CalibrationView
from PySide6.QtCore import Qt


# Ensure a QApplication instance for GUI testing
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
    assert view.grid_rows_input_1.value() == 9
    assert view.grid_cols_input_1.value() == 4
    assert view.image_label.text() == "No images loaded"


def test_grid_size_spinboxes(view):
    """Test the grid size spinboxes for pattern calibration."""
    view.grid_rows_input_1.setValue(12)
    view.grid_cols_input_1.setValue(8)

    assert view.grid_rows_input_1.value() == 12
    assert view.grid_cols_input_1.value() == 8


def test_button_clicks(view, qtbot):
    """Test button clicks to ensure widgets respond."""
    # Test Print Chessboard button
    qtbot.mouseClick(view.print_button, Qt.LeftButton)
    assert view.print_button.text() == "Print Chessboard"

    # Test Load Calibration Images button
    qtbot.mouseClick(view.load_button, Qt.LeftButton)
    assert view.image_label.text() in ["No images loaded", "Images loaded"]


def test_resolution_input(view):
    """Test the diagonal distance input for metric calibration."""
    view.diagonal_distance_value.setValue(150.0)
    assert view.diagonal_distance_value.value() == 150.0


def test_save_calibration_button(view, qtbot):
    """Test if the save calibration button is clickable."""
    qtbot.mouseClick(view.save_calibration_button, Qt.LeftButton)
    assert view.save_calibration_button.isEnabled()
