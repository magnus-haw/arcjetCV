import pytest
from PySide6.QtWidgets import QApplication
from PySide6 import QtWidgets
from PySide6.QtCore import Qt
from arcjetCV.gui.main_window import MainWindow
from pathlib import Path
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QMessageBox
from unittest.mock import patch


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
    target_index = (
        0  # Adjust this index based on your 'Extract Edges' tab's actual position
    )

    # Simulate mouse click on the tab to switch tabs
    tab_bar = app.ui.tabWidget.tabBar()
    tab_rect = tab_bar.tabRect(target_index)
    click_pos = tab_rect.center()

    # Adjust click position based on tab_bar geometry
    click_pos.setX(click_pos.x() + tab_bar.geometry().x())
    click_pos.setY(click_pos.y() + tab_bar.geometry().y())

    # Simulate mouse click on adjusted click position
    QTest.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)

    # Assert that the current index of the tab widget is now the 'Extract Edges' tab
    assert app.ui.tabWidget.currentIndex() == target_index


def test_load_video(app, qtbot, mocker):
    # Mock the QFileDialog.getOpenFileName method to return a test video path
    expected_video_path = (
        "/Users/alexandrequintart/NASA/arcjetCV_release/arcjetCV/tests/arcjet_test.mp4"
    )
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        return_value=(expected_video_path, ""),
    )

    # Simulate clicking the 'Load Video' button
    qtbot.mouseClick(app.ui.pushButton_loadVideo, Qt.LeftButton)

    # Check if the path attribute of your application is correctly updated
    assert app.path == expected_video_path

    # Optionally, check if other attributes related to video loading are correctly set
    assert app.VIDEO_LOADED is True
    assert app.video is not None
    assert app.videometa is not None


def test_select_flow_direction(app, qtbot):
    flow_direction_text = "left"
    direction_index = app.ui.comboBox_flowDirection.findText(flow_direction_text)
    assert direction_index != -1
    with qtbot.waitSignal(
        app.ui.comboBox_flowDirection.currentIndexChanged, timeout=1000
    ):
        app.ui.comboBox_flowDirection.setCurrentIndex(direction_index)
    assert app.ui.comboBox_flowDirection.currentText() == flow_direction_text


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
    assert app.ui.checkBox_display_shock.isChecked()
    # Simulate checking the 'Show Shock' checkbox
    qtbot.mouseClick(app.ui.checkBox_display_shock, Qt.LeftButton)

    # Verify that the checkbox is now checked and the shock is shown
    assert not app.ui.checkBox_display_shock.isChecked()
    # Simulate unchecking the 'Show Shock' checkbox
    qtbot.mouseClick(app.ui.checkBox_display_shock, Qt.LeftButton)

    # Verify that the checkbox is unchecked and the shock is no longer shown
    assert app.ui.checkBox_display_shock.isChecked()


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
    """
    Test applying a filter.
    """
    min_hue_value = 10
    max_hue_value = 20

    # Simulate setting values for minHue and maxHue spin boxes
    with qtbot.waitSignals([app.ui.minHue.valueChanged, app.ui.maxHue.valueChanged]):
        app.ui.minHue.setValue(min_hue_value)
        app.ui.maxHue.setValue(max_hue_value)

    assert app.ui.minHue.value() == min_hue_value
    assert app.ui.maxHue.value() == max_hue_value


def test_apply_crop(app, qtbot, mocker):
    """
    Test loading a video and then applying crop settings.
    """
    # Mock the QFileDialog.getOpenFileName method to return a test video path
    expected_video_path = (
        "/Users/alexandrequintart/NASA/arcjetCV_release/arcjetCV/tests/arcjet_test.mp4"
    )
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        return_value=(expected_video_path, ""),
    )

    # Simulate clicking the 'Load Video' button to load the video
    qtbot.mouseClick(app.ui.pushButton_loadVideo, Qt.LeftButton)

    # Ensure the video was loaded correctly
    assert app.path == expected_video_path
    assert app.VIDEO_LOADED is True
    assert app.video is not None
    assert app.videometa is not None

    # Set crop parameters via UI elements
    app.ui.spinBox_crop_xmin.setValue(100)
    app.ui.spinBox_crop_xmax.setValue(200)
    app.ui.spinBox_crop_ymin.setValue(100)
    app.ui.spinBox_crop_ymax.setValue(200)

    # Simulate clicking the 'Apply Crop' button or directly invoke the method
    qtbot.mouseClick(app.ui.applyCrop, Qt.LeftButton)
    # or if there is a specific method for applying crop in your application, call it directly

    # Verify crop parameters are correctly applied and reflected in the videometa
    expected_crop_settings = [[100, 200], [100, 200]]
    current_crop_settings = app.videometa.crop_range()

    # Assert that the current crop settings match the expected values
    assert (
        current_crop_settings == expected_crop_settings
    ), "Crop settings did not update as expected."


def test_toggle_show_crop_checkbox(app, qtbot, mocker):
    """
    Test the functionality of the 'Show Crop' checkbox.
    """
    # Mock the QFileDialog.getOpenFileName method to return a test video path
    expected_video_path = (
        "/Users/alexandrequintart/NASA/arcjetCV_release/arcjetCV/tests/arcjet_test.mp4"
    )
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        return_value=(expected_video_path, ""),
    )

    # Simulate clicking the 'Load Video' button to load the video
    qtbot.mouseClick(app.ui.pushButton_loadVideo, Qt.LeftButton)

    # Ensure the video was loaded correctly
    assert app.path == expected_video_path
    assert app.VIDEO_LOADED is True
    assert app.video is not None
    assert app.videometa is not None
    # Initial state check (assuming the checkbox starts unchecked and crop is not shown)
    assert app.ui.checkBox_crop.isChecked()
    # assert (
    #     not app.show_crop
    # )  # This should be replaced with your application's internal flag for showing crop

    # Simulate checking the 'Show Crop' checkbox
    qtbot.mouseClick(app.ui.checkBox_crop, Qt.LeftButton)

    # Verify that the checkbox is now checked and the crop is shown
    assert not app.ui.checkBox_crop.isChecked()
    # assert (
    #     app.show_crop
    # )  # Again, replace with your application's logic for showing/hiding crop

    # Simulate unchecking the 'Show Crop' checkbox
    qtbot.mouseClick(app.ui.checkBox_crop, Qt.LeftButton)

    # Verify that the checkbox is unchecked and the crop is no longer shown
    assert app.ui.checkBox_crop.isChecked()
    # assert not app.show_crop  # Adjust based on your application's behavior


def test_annotation_checkbox(app, qtbot, mocker):
    test_load_video(app, qtbot, mocker)
    assert app.ui.checkBox_annotate.isChecked()

    # Simulate clicking the checkbox to enable annotation
    qtbot.mouseClick(app.ui.checkBox_annotate, Qt.LeftButton)

    # Verify that the checkbox is now checked
    assert not app.ui.checkBox_annotate.isChecked()

    # Optionally, simulate clicking again to disable annotation
    qtbot.mouseClick(app.ui.checkBox_annotate, Qt.LeftButton)

    # Verify that the checkbox is now unchecked
    assert app.ui.checkBox_annotate.isChecked()


def test_apply_model_filter(app, qtbot, mocker):
    """
    Test setting model filter parameters and applying them.
    """
    test_load_video(app, qtbot, mocker)
    filter_index = app.ui.comboBox_filterType.findText("HSV")
    assert filter_index != -1
    with qtbot.waitSignal(app.ui.comboBox_filterType.currentIndexChanged, timeout=1000):
        app.ui.comboBox_filterType.setCurrentIndex(filter_index)
    assert app.ui.comboBox_filterType.currentIndex() == filter_index

    # Set model filter parameters
    app.ui.minHue.setValue(10)
    app.ui.maxHue.setValue(20)
    app.ui.minSaturation.setValue(30)
    app.ui.maxSaturation.setValue(40)
    app.ui.minIntensity.setValue(50)
    app.ui.maxIntensity.setValue(60)
    app.update_frame_index()
    # Then, assert that this range matches your expected values
    assert app.processor.HSVModelRange == [(10, 30, 50), (20, 40, 60)]


def test_apply_shock_filter(app, qtbot, mocker):
    """
    Test setting shock filter parameters and applying them.
    """
    test_load_video(app, qtbot, mocker)
    filter_index = app.ui.comboBox_filterType.findText("HSV")
    assert filter_index != -1
    with qtbot.waitSignal(app.ui.comboBox_filterType.currentIndexChanged, timeout=1000):
        app.ui.comboBox_filterType.setCurrentIndex(filter_index)
    assert app.ui.comboBox_filterType.currentIndex() == filter_index

    # Switch to the Shock Filter tab if necessary
    app.ui.FilterTabs.setCurrentIndex(1)  # Assuming index 1 is the Shock Filter tab

    # Set shock filter parameters
    app.ui.minHue_2.setValue(70)
    app.ui.maxHue_2.setValue(80)
    app.ui.minSaturation_2.setValue(90)
    app.ui.maxSaturation_2.setValue(100)
    app.ui.minIntensity_2.setValue(110)
    app.ui.maxIntensity_2.setValue(120)
    app.update_frame_index()

    assert app.processor.HSVShockRange == [(70, 90, 110), (80, 100, 120)]


def test_set_frame_range(app, qtbot, mocker):
    """
    Test setting the frame range for processing.
    """
    test_load_video(app, qtbot, mocker)
    # Set frame range values
    app.ui.spinBox_FirstGoodFrame.setValue(10)
    app.ui.spinBox_LastGoodFrame.setValue(100)
    with patch.object(QMessageBox, "exec", return_value=QMessageBox.Ok):
        # Call the method to be tested
        app.process_all()
    # Verify that the frame range values are set correctly
    assert app.videometa["FIRST_GOOD_FRAME"] == 10
    assert app.videometa["LAST_GOOD_FRAME"] == 100
    # Adjust the attribute names based on your application's implementation


def test_process_every_nth_frame(app, qtbot, mocker):
    """
    Test setting the application to process every Nth frame.
    """
    test_load_video(app, qtbot, mocker)
    with qtbot.waitSignal(app.ui.spinBox_frame_skips.valueChanged):
        app.ui.spinBox_frame_skips.setValue(10)
    assert app.ui.spinBox_frame_skips.value() == 10


def test_set_output_filename(app, qtbot, mocker):
    """
    Test setting the output filename.
    """
    test_load_video(app, qtbot, mocker)
    app.ui.lineEdit_filename.setText("output_filename")
    with patch.object(QMessageBox, "exec", return_value=QMessageBox.Ok):
        app.process_all()
    assert app.processor.filename == "output_filename_10_100.json"


def test_toggle_write_video(app, qtbot, mocker):
    """
    Test toggling the 'Write video?' checkbox.
    """
    test_load_video(app, qtbot, mocker)
    initial_state = app.ui.checkBox_writeVideo.isChecked()

    # Toggle the checkbox
    qtbot.mouseClick(app.ui.checkBox_writeVideo, Qt.LeftButton)

    # Verify the checkbox state is toggled
    assert app.ui.checkBox_writeVideo.isChecked() != initial_state


def test_process_all_button(app, qtbot, mocker):
    test_load_video(app, qtbot, mocker)
    qtbot.waitSignal(app.frame_processed, timeout=10000)

    # Call the method to be tested
    with patch.object(QMessageBox, "exec", return_value=QMessageBox.Ok):
        app.process_all()
    qtbot.wait(1000)

    # Assertion
    assert app.msg_box.text() == "The video has been processed."


# Analysis tab


def test_switch_to_analysis_tab(app, qtbot):
    # Assuming 'Analysis' tab is at index 1, adjust as per your application
    target_index = 1
    # Simulate mouse click on the tab to switch tabs
    tab_bar = app.ui.tabWidget.tabBar()
    tab_rect = tab_bar.tabRect(target_index)

    # Calculate click position as center of the tab
    click_pos = tab_rect.center()

    # Simulate mouse click on the tab
    qtbot.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)

    # Assert that the current index of the tab widget is now the 'Analysis' tab
    assert app.ui.tabWidget.currentIndex() == target_index


def test_load_analysis_files(app, qtbot, mocker):
    """
    Test loading files in the 'Analysis' tab and verifying UI updates.
    """
    expected_file_path = "/Users/alexandrequintart/NASA/arcjetCV_release/arcjetCV/tests/arcjet_test_0_800.json"
    expected_summary_start = (
        "Loaded 1 files"  # Assuming one file was selected for simplicity
    )

    # Mock the file dialog to return a predetermined file path
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileNames",
        return_value=([expected_file_path], ""),
    )

    # Trigger the file loading process
    qtbot.mouseClick(app.ui.pushButton_LoadFiles, Qt.LeftButton)

    # Check if the UI elements are updated to reflect the loaded files
    assert expected_summary_start in app.ui.label_data_summary.text()
    # Adjust assertion to match the final state of app.ui.basebar
    assert "Finished plotting data" == app.ui.basebar.text()


def test_plot_data_button(app, qtbot, mocker):
    """
    Test the 'Plot Data' button functionality in the 'Analysis' tab after loading analysis files.
    """
    # Mock the file dialog to return a predetermined file path, simulating the file loading process
    expected_file_path = [
        "/Users/alexandrequintart/NASA/arcjetCV_release/arcjetCV/tests/arcjet_test_0_800.json"
    ]
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileNames",
        return_value=(expected_file_path, ""),
    )

    # Simulate clicking the button that triggers loading of analysis files
    qtbot.mouseClick(app.ui.pushButton_LoadFiles, Qt.LeftButton)

    # After files are "loaded", simulate clicking the 'Plot Data' button
    qtbot.mouseClick(app.ui.pushButton_PlotData, Qt.LeftButton)

    # Verify that data plotting is initiated
    # This verification needs to be aligned with how your application indicates the plotting process has started or completed
    # For instance, if your application updates a label or a status bar, you might check its text
    assert (
        "Plotting data..." in app.ui.basebar.text()
        or "Finished plotting data" in app.ui.basebar.text()
    )

    # Additionally, if your application changes a state or sets a flag indicating plotting has started, check that instead
    # Example: assert app.is_plotting is True


def test_fit_data_button(app, qtbot, mocker):
    """
    Test the 'Fit Data' button functionality in the 'Analysis' tab.
    """
    # Pre-load analysis files or set up the necessary state before fitting
    test_load_analysis_files(app, qtbot, mocker)
    # Adjust method call as per your application
    qtbot.mouseClick(app.ui.pushButton_fitData, Qt.LeftButton)
    # Verify that data fitting is initiated, adjust based on your application's behavior
    # Check if self.fit_dict exists
    assert hasattr(app, "fit_dict")
    # Check if self.fit_dict is not empty
    assert app.fit_dict


def test_export_csv_plots_button(app, qtbot, mocker, tmp_path):
    """
    Test the 'Export CSV/plots' button functionality in the 'Analysis' tab.
    """
    test_load_analysis_files(app, qtbot, mocker)
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
    Test switching to the 'Plotting params' tab within the 'Plotting params' tab.
    """

    app.ui.tabWidget_2.setCurrentIndex(1)

    # Assuming 'Plotting params' tab is at index 1 within tabWidget_2
    target_index = 0

    # Simulate mouse click on the tab to switch tabs
    tab_bar = app.ui.tabWidget_2.tabBar()
    tab_rect = tab_bar.tabRect(target_index)
    click_pos = tab_rect.center()

    # Adjust click position based on tab_bar geometry
    click_pos.setX(click_pos.x() + tab_bar.geometry().x())
    click_pos.setY(click_pos.y() + tab_bar.geometry().y())

    # Simulate mouse click on adjusted click position
    QTest.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)

    # Assert that the current index of the tab widget is now the 'Plotting params' tab
    assert app.ui.tabWidget_2.currentIndex() == target_index


def test_set_model_diameter(app, qtbot):
    expected_diameter = 150
    with qtbot.waitSignal(app.ui.doubleSpinBox_diameter.valueChanged):
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


def test_toggle_display_shock(app, qtbot, mocker):
    # Simulate checking the 'Display Shock' checkbox
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_display_shock2.isChecked()
    qtbot.mouseClick(app.ui.checkBox_display_shock2, Qt.LeftButton)
    # Verify state changed
    assert app.ui.checkBox_display_shock2.isChecked() != initial_state


def test_switch_to_fitting_params_tab(app, qtbot):
    """
    Test switching to the 'Fitting params' tab within the 'Analysis' tab.
    """
    # Ensure we are in the 'Analysis' tab first
    app.ui.tabWidget.setCurrentIndex(0)  # Assuming 'Analysis' is at index 1

    # Assuming 'Fitting params' tab is at index 1 within tabWidget_2
    target_index = 1

    # Simulate mouse click on the tab to switch tabs
    tab_bar = app.ui.tabWidget_2.tabBar()
    tab_rect = tab_bar.tabRect(target_index)
    click_pos = tab_rect.center()

    # Adjust click position based on tab_bar geometry
    click_pos.setX(click_pos.x() + tab_bar.geometry().x())
    click_pos.setY(click_pos.y() + tab_bar.geometry().y())

    # Simulate mouse click on adjusted click position
    QTest.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)

    # Assert that the current index of the tab widget is now the 'Fitting params' tab
    assert app.ui.tabWidget_2.currentIndex() == target_index


def test_select_fit_type(app, qtbot):
    expected_fit_type = "linear"  # Assuming 'linear' is an option
    app.ui.comboBox_fit_type.setCurrentText(expected_fit_type)
    assert app.ui.comboBox_fit_type.currentText() == expected_fit_type


def test_set_fit_start_time(app, qtbot):
    expected_start_time = 0.0  # Example start time
    app.ui.doubleSpinBox_fit_start_time.setValue(expected_start_time)
    assert app.ui.doubleSpinBox_fit_start_time.value() == expected_start_time


def test_set_fit_end_time(app, qtbot):
    expected_end_time = 50  # Example end time
    app.ui.doubleSpinBox_fit_last_time.setValue(expected_end_time)
    assert app.ui.doubleSpinBox_fit_last_time.value() == expected_end_time


def test_toggle_checkbox_95_radius(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_95_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_95_radius, Qt.LeftButton)
    assert app.ui.checkBox_95_radius.isChecked() != initial_state


def test_toggle_checkbox_m50_radius(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_m50_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_m50_radius, Qt.LeftButton)
    assert app.ui.checkBox_m50_radius.isChecked() != initial_state


def test_toggle_checkbox_ypos(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_ypos.isChecked()
    qtbot.mouseClick(app.ui.checkBox_ypos, Qt.LeftButton)
    assert app.ui.checkBox_ypos.isChecked() != initial_state


def test_toggle_checkbox_50_radius(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_50_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_50_radius, Qt.LeftButton)
    assert app.ui.checkBox_50_radius.isChecked() != initial_state


def test_toggle_checkbox_shockmodel(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_shockmodel.isChecked()
    qtbot.mouseClick(app.ui.checkBox_shockmodel, Qt.LeftButton)
    assert app.ui.checkBox_shockmodel.isChecked() != initial_state


def test_toggle_checkbox_shock_center(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_shock_center.isChecked()
    qtbot.mouseClick(app.ui.checkBox_shock_center, Qt.LeftButton)
    assert app.ui.checkBox_shock_center.isChecked() != initial_state


def test_toggle_checkbox_model_center(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_model_center.isChecked()
    qtbot.mouseClick(app.ui.checkBox_model_center, Qt.LeftButton)
    assert app.ui.checkBox_model_center.isChecked() != initial_state


def test_toggle_checkbox_m95_radius(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_m95_radius.isChecked()
    qtbot.mouseClick(app.ui.checkBox_m95_radius, Qt.LeftButton)
    assert app.ui.checkBox_m95_radius.isChecked() != initial_state


def test_toggle_checkbox_model_rad(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_model_rad.isChecked()
    qtbot.mouseClick(app.ui.checkBox_model_rad, Qt.LeftButton)
    assert app.ui.checkBox_model_rad.isChecked() != initial_state


def test_toggle_checkbox_shock_area(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_shock_area.isChecked()
    qtbot.mouseClick(app.ui.checkBox_shock_area, Qt.LeftButton)
    assert app.ui.checkBox_shock_area.isChecked() != initial_state
