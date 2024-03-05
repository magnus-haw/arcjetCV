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


def test_switch_to_extract_edges_tab(app, qtbot):
    """
    Test switching to the 'Extract Edges' tab.
    """
    # Assuming 'Extract Edges' tab is at index 0, adjust as per your application
    qtbot.mouseClick(
        app.ui.tabWidget.tabBar().tabButton(
            0, QtWidgets.QTabBar.ButtonPosition.RightSide
        ),
        Qt.LeftButton,
    )
    assert app.ui.tabWidget.currentIndex() == 0


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


def test_toggle_show_shock_checkbox(app, qtbot):
    """
    Test the functionality of the 'Show Shock' checkbox.
    """
    # Initial state check (assuming the checkbox starts unchecked and shock is not shown)
    assert not app.ui.checkBox_display_shock.isChecked()
    assert (
        not app.display_shock
    )  # This should be replaced with your application's internal flag for showing shock

    # Simulate checking the 'Show Shock' checkbox
    qtbot.mouseClick(app.ui.checkBox_display_shock, Qt.LeftButton)

    # Verify that the checkbox is now checked and the shock is shown
    assert app.ui.checkBox_display_shock.isChecked()
    assert (
        app.display_shock
    )  # Again, replace with your application's logic for showing/hiding shock

    # Simulate unchecking the 'Show Shock' checkbox
    qtbot.mouseClick(app.ui.checkBox_display_shock, Qt.LeftButton)

    # Verify that the checkbox is unchecked and the shock is no longer shown
    assert not app.ui.checkBox_display_shock.isChecked()
    assert not app.display_shock  # Adjust based on your application's behavior


def test_switch_tabs(app, qtbot):
    """
    Test switching between the Crop, Model Filter, and Shock Filter tabs.
    """
    # Assuming the indexes of the tabs are known
    crop_tab_index = 0  # Adjust based on your application
    model_filter_tab_index = 1  # Adjust based on your application
    shock_filter_tab_index = 2  # Adjust based on your application

    # Switch to Crop tab and verify
    app.ui.FilterTabs.setCurrentIndex(crop_tab_index)
    assert app.ui.FilterTabs.currentIndex() == crop_tab_index

    # Switch to Model Filter tab and verify
    app.ui.FilterTabs.setCurrentIndex(model_filter_tab_index)
    assert app.ui.FilterTabs.currentIndex() == model_filter_tab_index

    # Switch to Shock Filter tab and verify
    app.ui.FilterTabs.setCurrentIndex(shock_filter_tab_index)
    assert app.ui.FilterTabs.currentIndex() == shock_filter_tab_index


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


def test_toggle_show_crop_checkbox(app, qtbot):
    """
    Test the functionality of the 'Show Crop' checkbox.
    """
    # Initial state check (assuming the checkbox starts unchecked and crop is not shown)
    assert not app.ui.checkBox_crop.isChecked()
    assert (
        not app.show_crop
    )  # This should be replaced with your application's internal flag for showing crop

    # Simulate checking the 'Show Crop' checkbox
    qtbot.mouseClick(app.ui.checkBox_crop, Qt.LeftButton)

    # Verify that the checkbox is now checked and the crop is shown
    assert app.ui.checkBox_crop.isChecked()
    assert (
        app.show_crop
    )  # Again, replace with your application's logic for showing/hiding crop

    # Simulate unchecking the 'Show Crop' checkbox
    qtbot.mouseClick(app.ui.checkBox_crop, Qt.LeftButton)

    # Verify that the checkbox is unchecked and the crop is no longer shown
    assert not app.ui.checkBox_crop.isChecked()
    assert not app.show_crop  # Adjust based on your application's behavior


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


# Analysis tab


def test_switch_to_analysis_tab(app, qtbot):
    """
    Test switching to the 'Analysis' tab.
    """
    # Assuming 'Analysis' tab is at index 1, adjust as per your application
    qtbot.mouseClick(
        app.ui.tabWidget.tabBar().tabButton(
            1, QtWidgets.QTabBar.ButtonPosition.RightSide
        ),
        Qt.LeftButton,
    )
    assert app.ui.tabWidget.currentIndex() == 1


def test_load_analysis_files(app, qtbot, mocker):
    """
    Test loading files in the 'Analysis' tab.
    """
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileNames",
        return_value=(
            ["/path/to/analysis_file1.json", "/path/to/analysis_file2.json"],
            "",
        ),
    )
    qtbot.mouseClick(app.ui.pushButton_LoadFiles, Qt.LeftButton)
    # Verify files are loaded, adjust attribute names based on your application
    assert "/path/to/analysis_file1.json" in app.loaded_files
    assert "/path/to/analysis_file2.json" in app.loaded_files


def test_plot_data_button(app, qtbot):
    """
    Test the 'Plot Data' button functionality in the 'Analysis' tab.
    """
    # Pre-load analysis files or set up the necessary state before plotting
    app.load_analysis_files(
        ["/path/to/analysis_file.json"]
    )  # Adjust method call as per your application
    qtbot.mouseClick(app.ui.pushButton_PlotData, Qt.LeftButton)
    # Verify that data plotting is initiated, adjust based on your application's behavior
    assert app.plotting_data  # Adjust attribute name as per your implementation


def test_fit_data_button(app, qtbot):
    """
    Test the 'Fit Data' button functionality in the 'Analysis' tab.
    """
    # Pre-load analysis files or set up the necessary state before fitting
    app.load_analysis_files(
        ["/path/to/analysis_file.json"]
    )  # Adjust method call as per your application
    qtbot.mouseClick(app.ui.pushButton_fitData, Qt.LeftButton)
    # Verify that data fitting is initiated, adjust based on your application's behavior
    assert app.fitting_data  # Adjust attribute name as per your implementation


def test_export_csv_plots_button(app, qtbot, mocker, tmp_path):
    """
    Test the 'Export CSV/plots' button functionality in the 'Analysis' tab.
    """
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getExistingDirectory",
        return_value=str(tmp_path),
    )
    qtbot.mouseClick(app.ui.pushButton_export_csv, Qt.LeftButton)
    # Verify that export is initiated and check for the existence of output files
    exported_files = list(tmp_path.glob("*"))  # Adjust as needed
    assert len(exported_files) > 0  # This assumes at least one file is exported




def test_switch_to_plotting_params_tab(app, qtbot):
    """
    Test switching to the 'Plotting params' tab within the 'Analysis' tab.
    """
    # Ensure we are in the 'Analysis' tab first
    app.ui.tabWidget.setCurrentIndex(1)  # Assuming 'Analysis' is at index 1
    # Assuming 'Plotting params' tab is at index 0 within tabWidget_2
    qtbot.mouseClick(
        app.ui.tabWidget_2.tabBar().tabButton(
            0, QtWidgets.QTabBar.ButtonPosition.RightSide
        ),
        Qt.LeftButton,
    )
    assert app.ui.tabWidget_2.currentIndex() == 0



def test_set_model_diameter(app, qtbot):
    expected_diameter = 150.0  # Example value
    app.ui.doubleSpinBox_diameter.setValue(expected_diameter)
    assert app.ui.doubleSpinBox_diameter.value() == expected_diameter

def test_set_length_units(app, qtbot):
    expected_units = "[mm]"  # Example unit
    app.ui.comboBox_units.setCurrentText(expected_units)
    assert app.ui.comboBox_units.currentText() == expected_units

def test_set_frames_per_second(app, qtbot):
    expected_fps = 60.0  # Example FPS value
    app.ui.doubleSpinBox_fps.setValue(expected_fps)
    assert app.ui.doubleSpinBox_fps.value() == expected_fps

def test_set_mask_nframes(app, qtbot):
    expected_mask_frames = 5  # Example value for masking n frames
    app.ui.spinBox_mask_frames.setValue(expected_mask_frames)
    assert app.ui.spinBox_mask_frames.value() == expected_mask_frames


def test_toggle_display_shock(app, qtbot):
    # Simulate checking the 'Display Shock' checkbox
    initial_state = app.ui.checkBox_display_shock2.isChecked()
    qtbot.mouseClick(app.ui.checkBox_display_shock2, Qt.LeftButton)
    # Verify state changed
    assert app.ui.checkBox_display_shock2.isChecked() != initial_state

def test_switch_to_fitting_params_tab(app, qtbot):
    """
    Test switching to the 'Fitting params' tab within the 'Analysis' tab.
    """
    # Ensure we are in the 'Analysis' tab first
    app.ui.tabWidget.setCurrentIndex(1)  # Assuming 'Analysis' is at index 1
    # Assuming 'Fitting params' tab is at index 1 within tabWidget_2
    qtbot.mouseClick(
        app.ui.tabWidget_2.tabBar().tabButton(
            1, QtWidgets.QTabBar.ButtonPosition.RightSide
        ),
        Qt.LeftButton,
    )
    assert app.ui.tabWidget_2.currentIndex() == 1

def test_select_fit_type(app, qtbot):
    expected_fit_type = "linear"  # Assuming 'linear' is an option
    app.ui.comboBox_fit_type.setCurrentText(expected_fit_type)
    assert app.ui.comboBox_fit_type.currentText() == expected_fit_type
 
 def test_set_fit_start_time(app, qtbot):
    expected_start_time = 0.0  # Example start time
    app.ui.doubleSpinBox_fit_start_time.setValue(expected_start_time)
    assert app.ui.doubleSpinBox_fit_start_time.value() == expected_start_time

def test_set_fit_end_time(app, qtbot):
    expected_end_time = 100.0  # Example end time
    app.ui.doubleSpinBox_fit_last_time.setValue(expected_end_time)
    assert app.ui.doubleSpinBox_fit_last_time.value() == expected_end_time


def test_toggle_checkbox_95_radius(app, qtbot):
    initial_state = app.ui.checkBox_95_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_95_radius, Qt.LeftButton)
    assert app.ui.checkBox_95_radius.isChecked() != initial_state

def test_toggle_checkbox_m50_radius(app, qtbot):
    initial_state = app.ui.checkBox_m50_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_m50_radius, Qt.LeftButton)
    assert app.ui.checkBox_m50_radius.isChecked() != initial_state

def test_toggle_checkbox_ypos(app, qtbot):
    initial_state = app.ui.checkBox_ypos.isChecked()
    qtbot.mouseClick(app.ui.checkBox_ypos, Qt.LeftButton)
    assert app.ui.checkBox_ypos.isChecked() != initial_state

def test_toggle_checkbox_50_radius(app, qtbot):
    initial_state = app.ui.checkBox_50_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_50_radius, Qt.LeftButton)
    assert app.ui.checkBox_50_radius.isChecked() != initial_state

def test_toggle_checkbox_shockmodel(app, qtbot):
    initial_state = app.ui.checkBox_shockmodel.isChecked()
    qtbot.mouseClick(app.ui.checkBox_shockmodel, Qt.LeftButton)
    assert app.ui.checkBox_shockmodel.isChecked() != initial_state

def test_toggle_checkbox_shock_center(app, qtbot):
    initial_state = app.ui.checkBox_shock_center.isChecked()
    qtbot.mouseClick(app.ui.checkBox_shock_center, Qt.LeftButton)
    assert app.ui.checkBox_shock_center.isChecked() != initial_state

def test_toggle_checkbox_model_center(app, qtbot):
    initial_state = app.ui.checkBox_model_center.isChecked()
    qtbot.mouseClick(app.ui.checkBox_model_center, Qt.LeftButton)
    assert app.ui.checkBox_model_center.isChecked() != initial_state

def test_toggle_checkbox_m95_radius(app, qtbot):
    # Note: This checkbox seems to be listed twice. Ensure unique names or only include it once.
    initial_state = app.ui.checkBox_m95_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_m95_radius, Qt.LeftButton)
    assert app.ui.checkBox_m95_radius.isChecked() != initial_state

def test_toggle_checkbox_model_rad(app, qtbot):
    initial_state = app.ui.checkBox_model_rad.isChecked()
    qtbot.mouseClick(app.ui.checkBox_model_rad, Qt.LeftButton)
    assert app.ui.checkBox_model_rad.isChecked() != initial_state

def test_toggle_checkbox_shock_area(app, qtbot):
    initial_state = app.ui.checkBox_shock_area.isChecked()
    qtbot.mouseClick(app.ui.checkBox_shock_area, Qt.LeftButton)
    assert app.ui.checkBox_shock_area.isChecked() != initial_state
