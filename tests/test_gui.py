import pytest
from arcjetCV.gui.main_window import MainWindow
from unittest.mock import patch
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from pathlib import Path
import os


def find_tests_path():
    project_root = Path(__file__).resolve().parent
    while (
        not (project_root / "setup.py").exists() and project_root.parent != project_root
    ):
        project_root = project_root.parent
    return str(project_root / "tests")


@pytest.fixture
def app(qtbot):
    test_app = QApplication.instance() if QApplication.instance() else QApplication([])
    window = MainWindow()
    window.testing = True
    qtbot.addWidget(window)
    window.hide()
    return window


def test_main_window_initialization(app):
    assert app.ui.pushButton_loadVideo.text() == "Load Video"


def test_switch_to_extract_edges_tab(app, qtbot):
    """
    Test switching to the 'Extract Edges' tab.
    """
    target_index = 0

    tab_bar = app.ui.tabWidget.tabBar()
    tab_rect = tab_bar.tabRect(target_index)
    click_pos = tab_rect.center()

    click_pos.setX(click_pos.x() + tab_bar.geometry().x())
    click_pos.setY(click_pos.y() + tab_bar.geometry().y())

    QTest.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)

    assert app.ui.tabWidget.currentIndex() == target_index


def test_load_video(app, qtbot, mocker):
    expected_video_path = os.path.join(find_tests_path(), "arcjet_test.mp4")
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        return_value=(expected_video_path, ""),
    )

    qtbot.mouseClick(app.ui.pushButton_loadVideo, Qt.LeftButton)

    assert app.path == expected_video_path
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


def test_toggle_display_shock(app, qtbot, mocker):
    initial_state = app.ui.checkBox_display_shock.setChecked(True)
    qtbot.mouseClick(app.ui.checkBox_display_shock, Qt.LeftButton)
    assert app.ui.checkBox_display_shock.isChecked() != initial_state


def test_switch_tabs(app, qtbot):
    """
    Test switching between the Crop, Model Filter, and Shock Filter tabs.
    """
    crop_tab_index = 0
    model_filter_tab_index = 1
    shock_filter_tab_index = 2

    app.ui.FilterTabs.setCurrentIndex(crop_tab_index)
    assert app.ui.FilterTabs.currentIndex() == crop_tab_index

    app.ui.FilterTabs.setCurrentIndex(model_filter_tab_index)
    assert app.ui.FilterTabs.currentIndex() == model_filter_tab_index

    app.ui.FilterTabs.setCurrentIndex(shock_filter_tab_index)
    assert app.ui.FilterTabs.currentIndex() == shock_filter_tab_index


def test_apply_filter(app, qtbot):
    """
    Test applying a filter.
    """
    min_hue_value = 10
    max_hue_value = 20

    with qtbot.waitSignals([app.ui.minHue.valueChanged, app.ui.maxHue.valueChanged]):
        app.ui.minHue.setValue(min_hue_value)
        app.ui.maxHue.setValue(max_hue_value)

    assert app.ui.minHue.value() == min_hue_value
    assert app.ui.maxHue.value() == max_hue_value


def test_apply_crop(app, qtbot, mocker):
    """
    Test loading a video and then applying crop settings.
    """
    expected_video_path = os.path.join(find_tests_path(), "arcjet_test.mp4")
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        return_value=(expected_video_path, ""),
    )

    qtbot.mouseClick(app.ui.pushButton_loadVideo, Qt.LeftButton)

    assert app.path == expected_video_path
    assert app.VIDEO_LOADED is True
    assert app.video is not None
    assert app.videometa is not None

    app.ui.spinBox_crop_xmin.setValue(100)
    app.ui.spinBox_crop_xmax.setValue(425)
    app.ui.spinBox_crop_ymin.setValue(10)
    app.ui.spinBox_crop_ymax.setValue(700)

    qtbot.mouseClick(app.ui.applyCrop, Qt.LeftButton)
    expected_crop_settings = [[10, 700], [100, 425]]
    current_crop_settings = app.videometa.crop_range()

    assert (
        current_crop_settings == expected_crop_settings
    ), "Crop settings did not update as expected."


def test_toggle_show_crop_checkbox(app, qtbot, mocker):
    """
    Test the functionality of the 'Show Crop' checkbox.
    """
    expected_video_path = os.path.join(find_tests_path(), "arcjet_test.mp4")
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileName",
        return_value=(expected_video_path, ""),
    )

    qtbot.mouseClick(app.ui.pushButton_loadVideo, Qt.LeftButton)

    assert app.path == expected_video_path
    assert app.VIDEO_LOADED is True
    assert app.video is not None
    assert app.videometa is not None
    assert app.ui.checkBox_crop.isChecked()
    qtbot.mouseClick(app.ui.checkBox_crop, Qt.LeftButton)

    assert not app.ui.checkBox_crop.isChecked()
    qtbot.mouseClick(app.ui.checkBox_crop, Qt.LeftButton)
    assert app.ui.checkBox_crop.isChecked()


def test_annotation_checkbox(app, qtbot, mocker):
    test_load_video(app, qtbot, mocker)
    assert app.ui.checkBox_annotate.isChecked()
    qtbot.mouseClick(app.ui.checkBox_annotate, Qt.LeftButton)
    assert not app.ui.checkBox_annotate.isChecked()
    qtbot.mouseClick(app.ui.checkBox_annotate, Qt.LeftButton)
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

    app.ui.minHue.setValue(10)
    app.ui.maxHue.setValue(20)
    app.ui.minSaturation.setValue(30)
    app.ui.maxSaturation.setValue(40)
    app.ui.minIntensity.setValue(50)
    app.ui.maxIntensity.setValue(60)
    app.update_frame_index()
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

    app.ui.FilterTabs.setCurrentIndex(1)

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
    app.ui.spinBox_FirstGoodFrame.setValue(150)
    app.ui.spinBox_LastGoodFrame.setValue(400)
    app.process_all()
    assert app.videometa["FIRST_GOOD_FRAME"] == 150
    assert app.videometa["LAST_GOOD_FRAME"] == 400


def test_process_every_nth_frame(app, qtbot, mocker):
    """
    Test setting the application to process every Nth frame.
    """
    test_load_video(app, qtbot, mocker)
    with qtbot.waitSignal(app.ui.spinBox_frame_skips.valueChanged):
        app.ui.spinBox_frame_skips.setValue(2)
    assert app.ui.spinBox_frame_skips.value() == 2


def test_set_output_filename(app, qtbot, mocker):
    """
    Test setting the output filename.
    """
    test_load_video(app, qtbot, mocker)
    app.ui.lineEdit_filename.setText("output_filename")
    app.process_all()
    assert app.processor.filename == "output_filename_150_400.json"


def test_toggle_write_video(app, qtbot, mocker):
    """
    Test toggling the 'Write video?' checkbox.
    """
    test_load_video(app, qtbot, mocker)
    initial_state = app.ui.checkBox_writeVideo.isChecked()

    qtbot.mouseClick(app.ui.checkBox_writeVideo, Qt.LeftButton)

    assert app.ui.checkBox_writeVideo.isChecked() != initial_state


def test_process_all_button(app, qtbot, mocker):
    test_load_video(app, qtbot, mocker)
    qtbot.waitSignal(app.frame_processed, timeout=10000)

    check = app.process_all()
    qtbot.wait(1000)

    assert check == True


# Analysis tab


def test_switch_to_analysis_tab(app, qtbot):
    target_index = 1
    tab_bar = app.ui.tabWidget.tabBar()
    tab_rect = tab_bar.tabRect(target_index)
    click_pos = tab_rect.center()
    qtbot.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)
    assert app.ui.tabWidget.currentIndex() == target_index


def test_load_analysis_files(app, qtbot, mocker):
    """
    Test loading files in the 'Analysis' tab and verifying UI updates.
    """
    expected_file_path = os.path.join(find_tests_path(), "arcjet_test_150_400.json")
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileNames",
        return_value=([expected_file_path], ""),
    )

    qtbot.mouseClick(app.ui.pushButton_LoadFiles, Qt.LeftButton)
    assert "Loaded 1 files" in app.ui.label_data_summary.text()
    assert "Finished plotting data" == app.ui.basebar.text()


def test_plot_data_button(app, qtbot, mocker):
    """
    Test the 'Plot Data' button functionality in the 'Analysis' tab after loading analysis files.
    """

    expected_file_path = os.path.join(find_tests_path(), "arcjet_test_150_400.json")
    mocker.patch(
        "PySide6.QtWidgets.QFileDialog.getOpenFileNames",
        return_value=([expected_file_path], ""),
    )

    qtbot.mouseClick(app.ui.pushButton_LoadFiles, Qt.LeftButton)
    qtbot.mouseClick(app.ui.pushButton_PlotData, Qt.LeftButton)

    assert (
        "Plotting data..." in app.ui.basebar.text()
        or "Finished plotting data" in app.ui.basebar.text()
    )


def test_fit_data_button(app, qtbot, mocker):
    """
    Test the 'Fit Data' button functionality in the 'Analysis' tab.
    """
    test_load_analysis_files(app, qtbot, mocker)
    qtbot.mouseClick(app.ui.pushButton_fitData, Qt.LeftButton)
    assert hasattr(app, "fit_dict")
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
    exported_files = list(tmp_path.glob("*"))
    assert len(exported_files) > 0


def test_switch_to_plotting_params_tab(app, qtbot):
    """
    Test switching to the 'Plotting params' tab within the 'Plotting params' tab.
    """

    app.ui.tabWidget_2.setCurrentIndex(1)
    target_index = 0
    tab_bar = app.ui.tabWidget_2.tabBar()
    tab_rect = tab_bar.tabRect(target_index)
    click_pos = tab_rect.center()

    click_pos.setX(click_pos.x() + tab_bar.geometry().x())
    click_pos.setY(click_pos.y() + tab_bar.geometry().y())

    QTest.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)

    assert app.ui.tabWidget_2.currentIndex() == target_index


def test_set_model_diameter(app, qtbot):
    expected_diameter = 150
    with qtbot.waitSignal(app.ui.doubleSpinBox_diameter.valueChanged):
        app.ui.doubleSpinBox_diameter.setValue(expected_diameter)
    assert app.ui.doubleSpinBox_diameter.value() == expected_diameter


def test_set_length_units(app, qtbot):
    expected_units = "[mm]"
    app.ui.comboBox_units.setCurrentText(expected_units)
    assert app.ui.comboBox_units.currentText() == expected_units


def test_set_frames_per_second(app, qtbot):
    expected_fps = 60.0
    app.ui.doubleSpinBox_fps.setValue(expected_fps)
    assert app.ui.doubleSpinBox_fps.value() == expected_fps


def test_set_mask_nframes(app, qtbot):
    expected_mask_frames = 5
    app.ui.spinBox_mask_frames.setValue(expected_mask_frames)
    assert app.ui.spinBox_mask_frames.value() == expected_mask_frames


def test_toggle_display_shock_2(app, qtbot, mocker):
    test_load_analysis_files(app, qtbot, mocker)
    initial_state = app.ui.checkBox_display_shock2.setChecked(True)
    qtbot.mouseClick(app.ui.checkBox_display_shock2, Qt.LeftButton)
    assert app.ui.checkBox_display_shock2.isChecked() != initial_state


def test_switch_to_fitting_params_tab(app, qtbot):
    """
    Test switching to the 'Fitting params' tab within the 'Analysis' tab.
    """
    app.ui.tabWidget.setCurrentIndex(0)
    target_index = 1

    tab_bar = app.ui.tabWidget_2.tabBar()
    tab_rect = tab_bar.tabRect(target_index)
    click_pos = tab_rect.center()

    click_pos.setX(click_pos.x() + tab_bar.geometry().x())
    click_pos.setY(click_pos.y() + tab_bar.geometry().y())

    QTest.mouseClick(tab_bar, Qt.LeftButton, pos=click_pos)

    assert app.ui.tabWidget_2.currentIndex() == target_index


def test_select_fit_type(app, qtbot):
    expected_fit_type = "linear"
    app.ui.comboBox_fit_type.setCurrentText(expected_fit_type)
    assert app.ui.comboBox_fit_type.currentText() == expected_fit_type


def test_set_fit_start_time(app, qtbot):
    expected_start_time = 0.0
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
