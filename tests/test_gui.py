import pytest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from arcjetCV.gui import MainWindow  # Adjust import path as needed


@pytest.fixture
def app(qtbot):
    test_app = QApplication.instance() if QApplication.instance() else QApplication([])
    window = MainWindow()
    qtbot.addWidget(window)
    return window


def test_main_window_initialization(app):
    # Assuming "Load Video" is the actual button text, replace "Expected Button Text" with it
    assert app.ui.pushButton_loadVideo.text() == "Load Video"


def test_load_video(app, qtbot, mocker):
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        return_value=("/path/to/video.mp4", ""),
    )
    qtbot.mouseClick(app.ui.pushButton_loadVideo, Qt.LeftButton)
    # This assertion needs to be adjusted based on how your application tracks a video load
    assert app.video_path == "/path/to/video.mp4"  # Adjust based on actual attribute


def test_select_flow_direction(app, qtbot):
    flow_direction_text = "right"
    direction_index = app.ui.comboBox_flowDirection.findText(flow_direction_text)
    assert direction_index != -1
    with qtbot.waitSignal(
        app.ui.comboBox_flowDirection.currentIndexChanged, timeout=1000
    ):
        app.ui.comboBox_flowDirection.setCurrentIndex(direction_index)
    assert app.ui.comboBox_flowDirection.currentText() == flow_direction_text


def test_process_all_button(app, qtbot, tmp_path):
    video_path = tmp_path / "sample_video.mp4"  # Use a temporary path for the video
    app.load_video(str(video_path))
    with qtbot.waitSignal(app.frame_processed, timeout=10000):
        qtbot.mouseClick(app.ui.pushButton_process, Qt.LeftButton)
    assert app.processor is not None  # Adjust based on your application's architecture


def test_select_filter(app, qtbot):
    filter_index = app.ui.comboBox_filterType.findText("AutoHSV")
    assert filter_index != -1
    with qtbot.waitSignal(app.ui.comboBox_filterType.currentIndexChanged, timeout=1000):
        app.ui.comboBox_filterType.setCurrentIndex(filter_index)
    assert app.ui.comboBox_filterType.currentIndex() == filter_index


def test_apply_filter(app, qtbot):
    # Example: Set minimum and maximum hue for a filter; adjust according to your UI elements
    app.ui.minHue.setValue(10)
    app.ui.maxHue.setValue(20)
    # Trigger filter application; adjust according to your application's logic
    # Example: qtbot.mouseClick(app.ui.applyFilterButton, Qt.LeftButton)
    # Verify filter application; adjust assertions to your application's storage of filter settings


def test_apply_crop(app, qtbot):
    """
    Test applying crop settings.
    """
    # Set crop parameters
    app.ui.spinBox_crop_xmin.setValue(100)
    app.ui.spinBox_crop_xmax.setValue(200)
    app.ui.spinBox_crop_ymin.setValue(100)
    app.ui.spinBox_crop_ymax.setValue(200)

    # Assuming there's a button or method to apply cropping
    qtbot.mouseClick(app.ui.applyCrop, Qt.LeftButton)

    # Verify crop parameters are applied; adjust based on your application's implementation
    assert app.processor.crop == [
        [100, 200],
        [100, 200],
    ]  # This is a placeholder, adjust as necessary

def test_annotation_checkbox(app, qtbot):
    # Initially check if the checkbox is unchecked
    assert not app.ui.checkBox_annotate.isChecked()

    # Simulate clicking the checkbox to enable annotation
    qtbot.mouseClick(app.ui.checkBox_annotate, Qt.LeftButton)

    # Verify that the checkbox is now checked
    assert app.ui.checkBox_annotate.isChecked()

    # Optionally, simulate clicking again to disable annotation
    qtbot.mouseClick(app.ui.checkBox_annotate, Qt.LeftButton)

    # Verify that the checkbox is now unchecked
    assert not app.ui.checkBox_annotate.isChecked()



def test_apply_model_filter(app, qtbot):
    """
    Test setting model filter parameters and applying them.
    """
    # Set model filter parameters
    app.ui.minHue.setValue(10)
    app.ui.maxHue.setValue(20)
    app.ui.minSaturation.setValue(30)
    app.ui.maxSaturation.setValue(40)
    app.ui.minIntensity.setValue(50)
    app.ui.maxIntensity.setValue(60)

    # Apply the model filter settings
    # If there's a specific method or button in your GUI to apply the filter, trigger it here
    # For example: qtbot.mouseClick(app.ui.someApplyFilterButton, Qt.LeftButton)
    # Here we assume the settings are applied immediately upon change

    # Verify the filter settings are applied correctly
    assert app.processor.model_filter_settings == {
        "hue": [10, 20],
        "saturation": [30, 40],
        "intensity": [50, 60],
    }  # Adjust based on actual data structure


def test_apply_shock_filter(app, qtbot):
    """
    Test setting shock filter parameters and applying them.
    """
    # Switch to the Shock Filter tab if necessary
    app.ui.FilterTabs.setCurrentIndex(1)  # Assuming index 1 is the Shock Filter tab

    # Set shock filter parameters
    app.ui.minHue_2.setValue(70)
    app.ui.maxHue_2.setValue(80)
    app.ui.minSaturation_2.setValue(90)
    app.ui.maxSaturation_2.setValue(100)
    app.ui.minIntensity_2.setValue(110)
    app.ui.maxIntensity_2.setValue(120)

    # Apply the shock filter settings
    # If there's a specific method or button in your GUI to apply the filter, trigger it here
    # For example: qtbot.mouseClick(app.ui.someApplyFilterButton, Qt.LeftButton)
    # Here we assume the settings are applied immediately upon change

    # Verify the filter settings are applied correctly
    assert app.processor.shock_filter_settings == {
        "hue": [70, 80],
        "saturation": [90, 100],
        "intensity": [110, 120],
    }  # Adjust based on actual data structure


def test_set_frame_range(app, qtbot):
    """
    Test setting the frame range for processing.
    """
    # Set frame range values
    app.ui.spinBox_FirstGoodFrame.setValue(10)
    app.ui.spinBox_LastGoodFrame.setValue(100)

    # Verify that the frame range values are set correctly
    assert app.videometa["FIRST_GOOD_FRAME"] == 10
    assert app.videometa["LAST_GOOD_FRAME"] == 100
    # Adjust the attribute names based on your application's implementation


def test_process_every_nth_frame(app, qtbot):
    """
    Test setting the application to process every Nth frame.
    """
    # Set the value for processing every Nth frame
    app.ui.spinBox_frame_skips.setValue(5)

    # Verify that the setting is applied correctly
    assert (
        app.processor.frame_skip == 5
    )  # Adjust the attribute name as per your application's implementation


def test_set_output_filename(app, qtbot):
    """
    Test setting the output filename.
    """
    # Set the output filename
    app.ui.lineEdit_filename.setText("output_filename")

    # Verify that the filename is set correctly
    assert (
        app.processor.output_filename == "output_filename"
    )  # Adjust the attribute name based on your application's implementation


def test_toggle_write_video(app, qtbot):
    """
    Test toggling the 'Write video?' checkbox.
    """
    # Initial state check
    initial_state = app.ui.checkBox_writeVideo.isChecked()

    # Toggle the checkbox
    qtbot.mouseClick(app.ui.checkBox_write_video, Qt.LeftButton)

    # Verify the checkbox state is toggled
    assert app.ui.checkBox_writeVideo.isChecked() != initial_state


def test_export_to_csv(app, qtbot, mocker, tmp_path):
    output_path = tmp_path / "output.csv"
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getSaveFileName",
        return_value=(str(output_path), ""),
    )
    qtbot.mouseClick(app.ui.pushButton_export_csv, Qt.LeftButton)
    assert output_path.exists()
    # Further validation of the CSV contents can be added here
