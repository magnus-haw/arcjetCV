# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arcjetCV.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (
    QCoreApplication,
    QDate,
    QDateTime,
    QLocale,
    QMetaObject,
    QObject,
    QPoint,
    QRect,
    QSize,
    QTime,
    QUrl,
    Qt,
)
from PySide6.QtGui import (
    QAction,
    QBrush,
    QColor,
    QConicalGradient,
    QCursor,
    QFont,
    QFontDatabase,
    QGradient,
    QIcon,
    QImage,
    QKeySequence,
    QLinearGradient,
    QPainter,
    QPalette,
    QPixmap,
    QRadialGradient,
    QTransform,
)
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLayout,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMenuBar,
    QProgressBar,
    QPushButton,
    QSizePolicy,
    QSpacerItem,
    QSpinBox,
    QStatusBar,
    QTabWidget,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from arcjetCV.calibration.calibration_view import CalibrationView
from arcjetCV.calibration.calibration_controller import CalibrationController
from arcjetCV.gui.custom_classes import MatplotlibWidget


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1175, 794)
        self.actionLoad_video = QAction(MainWindow)
        self.actionLoad_video.setObjectName("actionLoad_video")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionSave_Filter = QAction(MainWindow)
        self.actionSave_Filter.setObjectName("actionSave_Filter")
        self.actionLoad_Filter_2 = QAction(MainWindow)
        self.actionLoad_Filter_2.setObjectName("actionLoad_Filter_2")
        self.actionSave_Filter_2 = QAction(MainWindow)
        self.actionSave_Filter_2.setObjectName("actionSave_Filter_2")
        self.actionExit_2 = QAction(MainWindow)
        self.actionExit_2.setObjectName("actionExit_2")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")

        self.tab_8 = QWidget()
        self.tab_8.setObjectName("tab_8")

        # Create the CalibrationView instance
        self.calibration_view = CalibrationView()
        self.calibration_controller = CalibrationController(self.calibration_view)

        # Use a new layout for tab_8
        calibration_layout = QVBoxLayout(self.tab_8)  # Assign directly to the widget
        calibration_layout.addWidget(self.calibration_view)
        calibration_layout.setContentsMargins(0, 0, 0, 0)  # Optional for full expansion

        # Add tab_8 to the tab widget
        self.tabWidget.addTab(self.tab_8, "")

        self.tab = QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_8 = QHBoxLayout(self.tab)
        self.horizontalLayout_8.setObjectName("horizontalLayout_8")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.Window0 = MatplotlibWidget(self.tab)
        self.Window0.setObjectName("Window0")
        sizePolicy = QSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.Window0.sizePolicy().hasHeightForWidth())
        self.Window0.setSizePolicy(sizePolicy)
        self.Window0.setMinimumSize(QSize(731, 451))

        self.verticalLayout.addWidget(self.Window0)

        self.Window3 = MatplotlibWidget(self.tab)
        self.Window3.setObjectName("Window3")
        sizePolicy.setHeightForWidth(self.Window3.sizePolicy().hasHeightForWidth())
        self.Window3.setSizePolicy(sizePolicy)
        self.Window3.setMinimumSize(QSize(731, 100))
        self.Window3.setMaximumSize(QSize(16777215, 300))

        self.verticalLayout.addWidget(self.Window3)

        self.horizontalLayout_8.addLayout(self.verticalLayout)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.verticalLayout_6.setSizeConstraint(QLayout.SetDefaultConstraint)
        # self.pushButton_loadVideo = QPushButton(self.tab)
        # self.pushButton_loadVideo.setObjectName("pushButton_loadVideo")
        # sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        # sizePolicy1.setHorizontalStretch(0)
        # sizePolicy1.setVerticalStretch(0)
        # sizePolicy1.setHeightForWidth(
        #     self.pushButton_loadVideo.sizePolicy().hasHeightForWidth()
        # )
        # self.pushButton_loadVideo.setSizePolicy(sizePolicy1)

        # self.verticalLayout_6.addWidget(self.pushButton_loadVideo)

        self.pushButton_loadCalibration = QPushButton(self.tab)
        self.pushButton_loadCalibration.setObjectName("pushButton_loadCalibration")
        self.pushButton_loadCalibration.setText("Load Calibration")

        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.pushButton_loadCalibration.sizePolicy().hasHeightForWidth()
        )
        self.pushButton_loadCalibration.setSizePolicy(sizePolicy1)

        # Add the button to the layout
        self.verticalLayout_6.addWidget(self.pushButton_loadCalibration)

        # Add a QLabel below the button to display the loaded file path
        self.label_calibrationPath = QLabel(self.tab)
        self.label_calibrationPath.setObjectName("label_calibrationPath")
        self.label_calibrationPath.setText("Calibration Path: None")  # Default text

        # Set a smaller font and style for better display
        font = self.label_calibrationPath.font()
        font.setPointSize(9)
        self.label_calibrationPath.setFont(font)
        self.label_calibrationPath.setStyleSheet("color: gray;")  # Optional styling

        # Add the label to the layout
        self.verticalLayout_6.addWidget(self.label_calibrationPath)

        self.pushButton_loadVideo = QPushButton(self.tab)
        self.pushButton_loadVideo.setObjectName("pushButton_loadVideo")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(
            self.pushButton_loadVideo.sizePolicy().hasHeightForWidth()
        )
        self.pushButton_loadVideo.setSizePolicy(sizePolicy1)

        self.verticalLayout_6.addWidget(self.pushButton_loadVideo)

        self.verticalSpacer_4 = QSpacerItem(
            20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_6.addItem(self.verticalSpacer_4)

        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName("groupBox_2")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy2)
        self.groupBox_2.setMinimumSize(QSize(350, 0))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName("gridLayout_6")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName("label_3")

        self.gridLayout_6.addWidget(self.label_3, 1, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")

        self.gridLayout_6.addWidget(self.label_4, 2, 0, 1, 1)

        self.spinBox_FrameIndex = QSpinBox(self.groupBox_2)
        self.spinBox_FrameIndex.setObjectName("spinBox_FrameIndex")
        sizePolicy1.setHeightForWidth(
            self.spinBox_FrameIndex.sizePolicy().hasHeightForWidth()
        )
        self.spinBox_FrameIndex.setSizePolicy(sizePolicy1)
        self.spinBox_FrameIndex.setMaximum(100000)
        self.spinBox_FrameIndex.setValue(0)

        self.gridLayout_6.addWidget(self.spinBox_FrameIndex, 0, 1, 1, 1)

        self.label_display_shock = QLabel(self.groupBox_2)
        self.label_display_shock.setObjectName("label_display_shock")

        self.gridLayout_6.addWidget(self.label_display_shock, 3, 0, 1, 1)

        self.comboBox_flowDirection = QComboBox(self.groupBox_2)
        self.comboBox_flowDirection.addItem("")
        self.comboBox_flowDirection.addItem("")
        self.comboBox_flowDirection.addItem("")
        self.comboBox_flowDirection.addItem("")
        self.comboBox_flowDirection.setObjectName("comboBox_flowDirection")
        sizePolicy1.setHeightForWidth(
            self.comboBox_flowDirection.sizePolicy().hasHeightForWidth()
        )
        self.comboBox_flowDirection.setSizePolicy(sizePolicy1)

        self.gridLayout_6.addWidget(self.comboBox_flowDirection, 1, 1, 1, 1)

        self.checkBox_display_shock = QCheckBox(self.groupBox_2)
        self.checkBox_display_shock.setObjectName("checkBox_display_shock")
        self.checkBox_display_shock.setChecked(True)

        self.gridLayout_6.addWidget(self.checkBox_display_shock, 3, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")

        self.gridLayout_6.addWidget(self.label_7, 0, 0, 1, 1)

        self.comboBox_filterType = QComboBox(self.groupBox_2)
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.setObjectName("comboBox_filterType")
        sizePolicy1.setHeightForWidth(
            self.comboBox_filterType.sizePolicy().hasHeightForWidth()
        )
        self.comboBox_filterType.setSizePolicy(sizePolicy1)

        self.gridLayout_6.addWidget(self.comboBox_filterType, 2, 1, 1, 1)

        self.verticalLayout_5.addLayout(self.gridLayout_6)

        self.verticalSpacer_5 = QSpacerItem(
            20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_5.addItem(self.verticalSpacer_5)

        self.FilterTabs = QTabWidget(self.groupBox_2)
        self.FilterTabs.setObjectName("FilterTabs")
        sizePolicy3 = QSizePolicy(
            QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum
        )
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.FilterTabs.sizePolicy().hasHeightForWidth())
        self.FilterTabs.setSizePolicy(sizePolicy3)
        self.tab_7 = QWidget()
        self.tab_7.setObjectName("tab_7")
        self.layoutWidget_2 = QWidget(self.tab_7)
        self.layoutWidget_2.setObjectName("layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(0, 10, 311, 101))
        self.formLayout_8 = QFormLayout(self.layoutWidget_2)
        self.formLayout_8.setObjectName("formLayout_8")
        self.formLayout_8.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_8.setLabelAlignment(
            Qt.AlignRight | Qt.AlignTrailing | Qt.AlignVCenter
        )
        self.formLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_19 = QLabel(self.layoutWidget_2)
        self.label_19.setObjectName("label_19")

        self.formLayout_8.setWidget(0, QFormLayout.LabelRole, self.label_19)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName("horizontalLayout_18")
        self.spinBox_crop_xmax = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_xmax.setObjectName("spinBox_crop_xmax")
        self.spinBox_crop_xmax.setMaximum(10000)
        self.spinBox_crop_xmax.setValue(20)

        self.horizontalLayout_18.addWidget(self.spinBox_crop_xmax)

        self.spinBox_crop_xmin = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_xmin.setObjectName("spinBox_crop_xmin")
        self.spinBox_crop_xmin.setMaximum(10000)
        self.spinBox_crop_xmin.setValue(20)

        self.horizontalLayout_18.addWidget(self.spinBox_crop_xmin)

        self.formLayout_8.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout_18)

        self.label_21 = QLabel(self.layoutWidget_2)
        self.label_21.setObjectName("label_21")

        self.formLayout_8.setWidget(1, QFormLayout.LabelRole, self.label_21)

        self.applyCrop = QPushButton(self.layoutWidget_2)
        self.applyCrop.setObjectName("applyCrop")

        self.formLayout_8.setWidget(2, QFormLayout.LabelRole, self.applyCrop)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName("horizontalLayout_20")
        self.checkBox_crop = QCheckBox(self.layoutWidget_2)
        self.checkBox_crop.setObjectName("checkBox_crop")
        self.checkBox_crop.setChecked(True)
        self.checkBox_crop.setTristate(False)

        self.horizontalLayout_20.addWidget(self.checkBox_crop)

        self.checkBox_annotate = QCheckBox(self.layoutWidget_2)
        self.checkBox_annotate.setObjectName("checkBox_annotate")
        self.checkBox_annotate.setChecked(True)

        self.horizontalLayout_20.addWidget(self.checkBox_annotate)

        self.formLayout_8.setLayout(2, QFormLayout.FieldRole, self.horizontalLayout_20)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName("horizontalLayout_19")
        self.spinBox_crop_ymax = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_ymax.setObjectName("spinBox_crop_ymax")
        self.spinBox_crop_ymax.setMaximum(10000)
        self.spinBox_crop_ymax.setValue(100)

        self.horizontalLayout_19.addWidget(self.spinBox_crop_ymax)

        self.spinBox_crop_ymin = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_ymin.setObjectName("spinBox_crop_ymin")
        self.spinBox_crop_ymin.setMaximum(10000)
        self.spinBox_crop_ymin.setValue(100)

        self.horizontalLayout_19.addWidget(self.spinBox_crop_ymin)

        self.formLayout_8.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout_19)

        self.FilterTabs.addTab(self.tab_7, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName("tab_3")
        self.verticalLayout_2 = QVBoxLayout(self.tab_3)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.label_8 = QLabel(self.tab_3)
        self.label_8.setObjectName("label_8")

        self.gridLayout_8.addWidget(self.label_8, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.minHue = QSpinBox(self.tab_3)
        self.minHue.setObjectName("minHue")
        self.minHue.setMaximum(180)
        self.minHue.setValue(0)

        self.horizontalLayout_3.addWidget(self.minHue)

        self.maxHue = QSpinBox(self.tab_3)
        self.maxHue.setObjectName("maxHue")
        self.maxHue.setMaximum(180)
        self.maxHue.setValue(121)

        self.horizontalLayout_3.addWidget(self.maxHue)

        self.gridLayout_8.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)

        self.label_9 = QLabel(self.tab_3)
        self.label_9.setObjectName("label_9")

        self.gridLayout_8.addWidget(self.label_9, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.minSaturation = QSpinBox(self.tab_3)
        self.minSaturation.setObjectName("minSaturation")
        self.minSaturation.setMaximum(255)
        self.minSaturation.setValue(0)

        self.horizontalLayout_4.addWidget(self.minSaturation)

        self.maxSaturation = QSpinBox(self.tab_3)
        self.maxSaturation.setObjectName("maxSaturation")
        self.maxSaturation.setMaximum(255)
        self.maxSaturation.setValue(125)

        self.horizontalLayout_4.addWidget(self.maxSaturation)

        self.gridLayout_8.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)

        self.label_5 = QLabel(self.tab_3)
        self.label_5.setObjectName("label_5")

        self.gridLayout_8.addWidget(self.label_5, 2, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.minIntensity = QSpinBox(self.tab_3)
        self.minIntensity.setObjectName("minIntensity")
        self.minIntensity.setMaximum(254)
        self.minIntensity.setValue(150)

        self.horizontalLayout_2.addWidget(self.minIntensity)

        self.maxIntensity = QSpinBox(self.tab_3)
        self.maxIntensity.setObjectName("maxIntensity")
        self.maxIntensity.setMaximum(255)
        self.maxIntensity.setValue(255)

        self.horizontalLayout_2.addWidget(self.maxIntensity)

        self.gridLayout_8.addLayout(self.horizontalLayout_2, 2, 1, 1, 1)

        self.verticalLayout_2.addLayout(self.gridLayout_8)

        self.FilterTabs.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName("tab_4")
        self.horizontalLayout_9 = QHBoxLayout(self.tab_4)
        self.horizontalLayout_9.setObjectName("horizontalLayout_9")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_15 = QLabel(self.tab_4)
        self.label_15.setObjectName("label_15")

        self.gridLayout_7.addWidget(self.label_15, 0, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName("horizontalLayout_6")
        self.minHue_2 = QSpinBox(self.tab_4)
        self.minHue_2.setObjectName("minHue_2")
        self.minHue_2.setMaximum(180)
        self.minHue_2.setValue(125)

        self.horizontalLayout_6.addWidget(self.minHue_2)

        self.maxHue_2 = QSpinBox(self.tab_4)
        self.maxHue_2.setObjectName("maxHue_2")
        self.maxHue_2.setMaximum(180)
        self.maxHue_2.setValue(170)

        self.horizontalLayout_6.addWidget(self.maxHue_2)

        self.gridLayout_7.addLayout(self.horizontalLayout_6, 0, 1, 1, 1)

        self.label_16 = QLabel(self.tab_4)
        self.label_16.setObjectName("label_16")

        self.gridLayout_7.addWidget(self.label_16, 1, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName("horizontalLayout_7")
        self.minSaturation_2 = QSpinBox(self.tab_4)
        self.minSaturation_2.setObjectName("minSaturation_2")
        self.minSaturation_2.setMaximum(255)
        self.minSaturation_2.setValue(40)

        self.horizontalLayout_7.addWidget(self.minSaturation_2)

        self.maxSaturation_2 = QSpinBox(self.tab_4)
        self.maxSaturation_2.setObjectName("maxSaturation_2")
        self.maxSaturation_2.setMaximum(255)
        self.maxSaturation_2.setValue(80)

        self.horizontalLayout_7.addWidget(self.maxSaturation_2)

        self.gridLayout_7.addLayout(self.horizontalLayout_7, 1, 1, 1, 1)

        self.label_6 = QLabel(self.tab_4)
        self.label_6.setObjectName("label_6")

        self.gridLayout_7.addWidget(self.label_6, 2, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.minIntensity_2 = QSpinBox(self.tab_4)
        self.minIntensity_2.setObjectName("minIntensity_2")
        self.minIntensity_2.setMaximum(254)
        self.minIntensity_2.setValue(85)

        self.horizontalLayout_5.addWidget(self.minIntensity_2)

        self.maxIntensity_2 = QSpinBox(self.tab_4)
        self.maxIntensity_2.setObjectName("maxIntensity_2")
        self.maxIntensity_2.setMaximum(255)
        self.maxIntensity_2.setValue(230)

        self.horizontalLayout_5.addWidget(self.maxIntensity_2)

        self.gridLayout_7.addLayout(self.horizontalLayout_5, 2, 1, 1, 1)

        self.horizontalLayout_9.addLayout(self.gridLayout_7)

        self.FilterTabs.addTab(self.tab_4, "")

        self.verticalLayout_5.addWidget(self.FilterTabs)

        self.verticalLayout_6.addWidget(self.groupBox_2)

        self.pushButton_save_frame = QPushButton(self.tab)
        self.pushButton_save_frame.setObjectName("pushButton_save_frame")

        self.verticalLayout_6.addWidget(self.pushButton_save_frame)

        self.verticalSpacer = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName("groupBox")
        sizePolicy3.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy3)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.label_17 = QLabel(self.groupBox)
        self.label_17.setObjectName("label_17")

        self.gridLayout_5.addWidget(self.label_17, 0, 0, 1, 1)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName("horizontalLayout_10")
        self.spinBox_FirstGoodFrame = QSpinBox(self.groupBox)
        self.spinBox_FirstGoodFrame.setObjectName("spinBox_FirstGoodFrame")
        self.spinBox_FirstGoodFrame.setMaximum(100000)
        self.spinBox_FirstGoodFrame.setValue(0)

        self.horizontalLayout_10.addWidget(self.spinBox_FirstGoodFrame)

        self.spinBox_LastGoodFrame = QSpinBox(self.groupBox)
        self.spinBox_LastGoodFrame.setObjectName("spinBox_LastGoodFrame")
        self.spinBox_LastGoodFrame.setMaximum(100000)
        self.spinBox_LastGoodFrame.setValue(0)

        self.horizontalLayout_10.addWidget(self.spinBox_LastGoodFrame)

        self.gridLayout_5.addLayout(self.horizontalLayout_10, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName("label_10")

        self.gridLayout_5.addWidget(self.label_10, 1, 0, 1, 1)

        self.spinBox_frame_skips = QSpinBox(self.groupBox)
        self.spinBox_frame_skips.setObjectName("spinBox_frame_skips")
        self.spinBox_frame_skips.setMinimum(1)
        self.spinBox_frame_skips.setMaximum(200)
        self.spinBox_frame_skips.setValue(5)

        self.gridLayout_5.addWidget(self.spinBox_frame_skips, 1, 1, 1, 1)

        self.label_20 = QLabel(self.groupBox)
        self.label_20.setObjectName("label_20")

        self.gridLayout_5.addWidget(self.label_20, 2, 0, 1, 1)

        self.lineEdit_filename = QLineEdit(self.groupBox)
        self.lineEdit_filename.setObjectName("lineEdit_filename")
        sizePolicy1.setHeightForWidth(
            self.lineEdit_filename.sizePolicy().hasHeightForWidth()
        )
        self.lineEdit_filename.setSizePolicy(sizePolicy1)

        self.gridLayout_5.addWidget(self.lineEdit_filename, 2, 1, 1, 1)

        self.verticalLayout_3.addLayout(self.gridLayout_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.checkBox_writeVideo = QCheckBox(self.groupBox)
        self.checkBox_writeVideo.setObjectName("checkBox_writeVideo")

        self.horizontalLayout.addWidget(self.checkBox_writeVideo)

        self.pushButton_process = QPushButton(self.groupBox)
        self.pushButton_process.setObjectName("pushButton_process")

        self.horizontalLayout.addWidget(self.pushButton_process)

        self.verticalLayout_3.addLayout(self.horizontalLayout)

        self.verticalLayout_6.addWidget(self.groupBox)

        # Add the progress bar below the "Process All" button (inside groupBox)
        self.progressBar = QProgressBar(self.centralwidget)  # Attach to central widget
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setMinimum(0)
        self.progressBar.setMaximum(100)
        self.progressBar.setValue(0)
        self.progressBar.setTextVisible(True)

        # Add progress bar below groupBox
        self.verticalLayout_6.addWidget(self.progressBar)

        self.horizontalLayout_8.addLayout(self.verticalLayout_6)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_11 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_11.setObjectName("horizontalLayout_11")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName("verticalLayout_8")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName("horizontalLayout_12")
        self.horizontalLayout_12.setSizeConstraint(QLayout.SetMaximumSize)
        self.Window1 = MatplotlibWidget(self.tab_2)
        self.Window1.setObjectName("Window1")
        sizePolicy.setHeightForWidth(self.Window1.sizePolicy().hasHeightForWidth())
        self.Window1.setSizePolicy(sizePolicy)
        self.Window1.setMinimumSize(QSize(400, 350))

        self.horizontalLayout_12.addWidget(self.Window1)

        self.Window2 = MatplotlibWidget(self.tab_2)
        self.Window2.setObjectName("Window2")
        sizePolicy.setHeightForWidth(self.Window2.sizePolicy().hasHeightForWidth())
        self.Window2.setSizePolicy(sizePolicy)
        self.Window2.setMinimumSize(QSize(400, 350))

        self.horizontalLayout_12.addWidget(self.Window2)

        self.verticalLayout_8.addLayout(self.horizontalLayout_12)

        self.textBrowser = QTextBrowser(self.tab_2)
        self.textBrowser.setObjectName("textBrowser")
        sizePolicy.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy)
        self.textBrowser.setMaximumSize(QSize(16777215, 250))

        self.verticalLayout_8.addWidget(self.textBrowser)

        self.horizontalLayout_11.addLayout(self.verticalLayout_8)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.verticalLayout_7.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName("horizontalLayout_13")
        self.pushButton_LoadFiles = QPushButton(self.tab_2)
        self.pushButton_LoadFiles.setObjectName("pushButton_LoadFiles")

        self.horizontalLayout_13.addWidget(self.pushButton_LoadFiles)

        self.pushButton_export_csv = QPushButton(self.tab_2)
        self.pushButton_export_csv.setObjectName("pushButton_export_csv")

        self.horizontalLayout_13.addWidget(self.pushButton_export_csv)

        self.verticalLayout_7.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName("horizontalLayout_15")
        self.pushButton_PlotData = QPushButton(self.tab_2)
        self.pushButton_PlotData.setObjectName("pushButton_PlotData")

        self.horizontalLayout_15.addWidget(self.pushButton_PlotData)

        self.pushButton_fitData = QPushButton(self.tab_2)
        self.pushButton_fitData.setObjectName("pushButton_fitData")

        self.horizontalLayout_15.addWidget(self.pushButton_fitData)

        self.verticalLayout_7.addLayout(self.horizontalLayout_15)

        self.verticalSpacer_6 = QSpacerItem(
            20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_7.addItem(self.verticalSpacer_6)

        self.tabWidget_2 = QTabWidget(self.tab_2)
        self.tabWidget_2.setObjectName("tabWidget_2")
        sizePolicy3.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy3)
        self.tab_5 = QWidget()
        self.tab_5.setObjectName("tab_5")
        self.gridLayout_2 = QGridLayout(self.tab_5)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.label_11 = QLabel(self.tab_5)
        self.label_11.setObjectName("label_11")

        self.gridLayout_2.addWidget(self.label_11, 1, 0, 1, 1)

        self.comboBox_units = QComboBox(self.tab_5)
        self.comboBox_units.addItem("")
        self.comboBox_units.addItem("")
        self.comboBox_units.addItem("")
        self.comboBox_units.addItem("")
        self.comboBox_units.setObjectName("comboBox_units")

        self.gridLayout_2.addWidget(self.comboBox_units, 1, 1, 1, 1)

        self.label_18 = QLabel(self.tab_5)
        self.label_18.setObjectName("label_18")

        self.gridLayout_2.addWidget(self.label_18, 2, 0, 1, 1)

        self.doubleSpinBox_fps = QDoubleSpinBox(self.tab_5)
        self.doubleSpinBox_fps.setObjectName("doubleSpinBox_fps")
        self.doubleSpinBox_fps.setMinimum(1.000000000000000)
        self.doubleSpinBox_fps.setMaximum(120.000000000000000)
        self.doubleSpinBox_fps.setValue(30.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_fps, 2, 1, 1, 1)

        self.label_2 = QLabel(self.tab_5)
        self.label_2.setObjectName("label_2")
        self.label_2.setMaximumSize(QSize(100, 30))

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)

        self.spinBox_mask_frames = QSpinBox(self.tab_5)
        self.spinBox_mask_frames.setObjectName("spinBox_mask_frames")
        self.spinBox_mask_frames.setMinimumSize(QSize(0, 0))
        self.spinBox_mask_frames.setMaximumSize(QSize(150, 30))
        self.spinBox_mask_frames.setMinimum(1)
        self.spinBox_mask_frames.setMaximum(1000)
        self.spinBox_mask_frames.setValue(10)

        self.gridLayout_2.addWidget(self.spinBox_mask_frames, 3, 1, 1, 1)

        self.label_display_shock2 = QLabel(self.tab_5)
        self.label_display_shock2.setObjectName("label_display_shock2")

        self.gridLayout_2.addWidget(self.label_display_shock2, 4, 0, 1, 1)

        self.checkBox_display_shock2 = QCheckBox(self.tab_5)
        self.checkBox_display_shock2.setObjectName("checkBox_display_shock2")
        self.checkBox_display_shock2.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_display_shock2, 4, 1, 1, 1)

        self.tabWidget_2.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName("tab_6")
        self.verticalLayout_10 = QVBoxLayout(self.tab_6)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.groupBox_3 = QGroupBox(self.tab_6)
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_12 = QLabel(self.groupBox_3)
        self.label_12.setObjectName("label_12")

        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 1)

        self.comboBox_fit_type = QComboBox(self.groupBox_3)
        self.comboBox_fit_type.addItem("")
        self.comboBox_fit_type.setObjectName("comboBox_fit_type")

        self.gridLayout_3.addWidget(self.comboBox_fit_type, 0, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox_3)
        self.label_13.setObjectName("label_13")

        self.gridLayout_3.addWidget(self.label_13, 1, 0, 1, 1)

        self.doubleSpinBox_fit_start_time = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_fit_start_time.setObjectName("doubleSpinBox_fit_start_time")

        self.gridLayout_3.addWidget(self.doubleSpinBox_fit_start_time, 1, 1, 1, 1)

        self.label_14 = QLabel(self.groupBox_3)
        self.label_14.setObjectName("label_14")

        self.gridLayout_3.addWidget(self.label_14, 2, 0, 1, 1)

        self.doubleSpinBox_fit_last_time = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_fit_last_time.setObjectName("doubleSpinBox_fit_last_time")

        self.gridLayout_3.addWidget(self.doubleSpinBox_fit_last_time, 2, 1, 1, 1)

        self.verticalLayout_10.addWidget(self.groupBox_3)

        self.tabWidget_2.addTab(self.tab_6, "")

        self.verticalLayout_7.addWidget(self.tabWidget_2)

        self.verticalSpacer_7 = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_7.addItem(self.verticalSpacer_7)

        self.groupBox_XT_params = QGroupBox(self.tab_2)
        self.groupBox_XT_params.setObjectName("groupBox_XT_params")
        self.gridLayout = QGridLayout(self.groupBox_XT_params)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox_shock_center = QCheckBox(self.groupBox_XT_params)
        self.checkBox_shock_center.setObjectName("checkBox_shock_center")

        self.gridLayout.addWidget(self.checkBox_shock_center, 2, 1, 1, 1)

        self.checkBox_m95_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_m95_radius.setObjectName("checkBox_m95_radius")
        self.checkBox_m95_radius.setChecked(False)
        self.checkBox_m95_radius.setTristate(False)

        self.gridLayout.addWidget(self.checkBox_m95_radius, 0, 0, 1, 1)

        self.checkBox_shockmodel = QCheckBox(self.groupBox_XT_params)
        self.checkBox_shockmodel.setObjectName("checkBox_shockmodel")

        self.gridLayout.addWidget(self.checkBox_shockmodel, 3, 1, 1, 1)

        self.checkBox_ypos = QCheckBox(self.groupBox_XT_params)
        self.checkBox_ypos.setObjectName("checkBox_ypos")

        self.gridLayout.addWidget(self.checkBox_ypos, 4, 1, 1, 1)

        self.checkBox_m50_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_m50_radius.setObjectName("checkBox_m50_radius")
        self.checkBox_m50_radius.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_m50_radius, 1, 0, 1, 1)

        self.checkBox_shock_area = QCheckBox(self.groupBox_XT_params)
        self.checkBox_shock_area.setObjectName("checkBox_shock_area")

        self.gridLayout.addWidget(self.checkBox_shock_area, 0, 1, 1, 1)

        self.checkBox_95_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_95_radius.setObjectName("checkBox_95_radius")
        self.checkBox_95_radius.setChecked(False)

        self.gridLayout.addWidget(self.checkBox_95_radius, 4, 0, 1, 1)

        self.checkBox_model_center = QCheckBox(self.groupBox_XT_params)
        self.checkBox_model_center.setObjectName("checkBox_model_center")
        self.checkBox_model_center.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_model_center, 2, 0, 1, 1)

        self.checkBox_50_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_50_radius.setObjectName("checkBox_50_radius")
        self.checkBox_50_radius.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_50_radius, 3, 0, 1, 1)

        self.checkBox_model_rad = QCheckBox(self.groupBox_XT_params)
        self.checkBox_model_rad.setObjectName("checkBox_model_rad")

        self.gridLayout.addWidget(self.checkBox_model_rad, 1, 1, 1, 1)

        self.verticalLayout_7.addWidget(self.groupBox_XT_params)

        self.verticalSpacer_8 = QSpacerItem(
            20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed
        )

        self.verticalLayout_7.addItem(self.verticalSpacer_8)

        self.groupBox_data_summary = QGroupBox(self.tab_2)
        self.groupBox_data_summary.setObjectName("groupBox_data_summary")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_data_summary)
        self.verticalLayout_9.setObjectName("verticalLayout_9")
        self.label_data_summary = QLabel(self.groupBox_data_summary)
        self.label_data_summary.setObjectName("label_data_summary")

        self.verticalLayout_9.addWidget(self.label_data_summary)

        self.verticalLayout_7.addWidget(self.groupBox_data_summary)

        self.verticalSpacer_2 = QSpacerItem(
            20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding
        )

        self.verticalLayout_7.addItem(self.verticalSpacer_2)

        self.horizontalLayout_11.addLayout(self.verticalLayout_7)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_4.addWidget(self.tabWidget)

        self.basebar = QLabel(self.centralwidget)
        self.basebar.setObjectName("basebar")

        self.verticalLayout_4.addWidget(self.basebar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName("menubar")
        self.menubar.setGeometry(QRect(0, 0, 1175, 24))
        self.menuMenu = QMenu(self.menubar)
        self.menuMenu.setObjectName("menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(Qt.ToolBarArea.TopToolBarArea, self.toolBar)

        self.menubar.addAction(self.menuMenu.menuAction())
        self.menuMenu.addAction(self.actionLoad_video)
        self.menuMenu.addAction(self.actionExit_2)

        self.retranslateUi(MainWindow)

        self.tabWidget.setCurrentIndex(1)
        self.FilterTabs.setCurrentIndex(1)
        self.tabWidget_2.setCurrentIndex(0)
        self.comboBox_units.setCurrentIndex(2)

        QMetaObject.connectSlotsByName(MainWindow)

    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(
            QCoreApplication.translate("MainWindow", "MainWindow", None)
        )
        self.actionLoad_video.setText(
            QCoreApplication.translate("MainWindow", "Load video", None)
        )
        self.actionExit.setText(QCoreApplication.translate("MainWindow", "Exit", None))
        self.actionSave_Filter.setText(
            QCoreApplication.translate("MainWindow", "Save Filter", None)
        )
        self.actionLoad_Filter_2.setText(
            QCoreApplication.translate("MainWindow", "Load Filter", None)
        )
        self.actionSave_Filter_2.setText(
            QCoreApplication.translate("MainWindow", "Save Filter", None)
        )
        self.actionExit_2.setText(
            QCoreApplication.translate("MainWindow", "Exit", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_8),
            QCoreApplication.translate("MainWindow", "Calibrate", None),
        )
        self.pushButton_loadVideo.setText(
            QCoreApplication.translate("MainWindow", "Load Video", None)
        )
        self.groupBox_2.setTitle(
            QCoreApplication.translate("MainWindow", "Input parameters", None)
        )
        self.label_3.setText(
            QCoreApplication.translate("MainWindow", "Flow direction:", None)
        )
        self.label_4.setText(
            QCoreApplication.translate("MainWindow", "Filter Method:", None)
        )
        self.label_display_shock.setText(
            QCoreApplication.translate("MainWindow", "Display Shock?", None)
        )
        self.comboBox_flowDirection.setItemText(
            0, QCoreApplication.translate("MainWindow", "right", None)
        )
        self.comboBox_flowDirection.setItemText(
            1, QCoreApplication.translate("MainWindow", "left", None)
        )
        self.comboBox_flowDirection.setItemText(
            2, QCoreApplication.translate("MainWindow", "up", None)
        )
        self.comboBox_flowDirection.setItemText(
            3, QCoreApplication.translate("MainWindow", "down", None)
        )
        self.checkBox_display_shock.setText("")
        self.label_7.setText(
            QCoreApplication.translate("MainWindow", "Frame Index:", None)
        )
        self.comboBox_filterType.setItemText(
            0, QCoreApplication.translate("MainWindow", "CNN", None)
        )
        self.comboBox_filterType.setItemText(
            1, QCoreApplication.translate("MainWindow", "AutoHSV", None)
        )
        self.comboBox_filterType.setItemText(
            2, QCoreApplication.translate("MainWindow", "HSV", None)
        )
        self.comboBox_filterType.setItemText(
            3, QCoreApplication.translate("MainWindow", "GRAY", None)
        )

        self.label_19.setText(
            QCoreApplication.translate("MainWindow", "X (min:max)", None)
        )
        self.label_21.setText(
            QCoreApplication.translate("MainWindow", "Y (min:max)", None)
        )
        self.applyCrop.setText(QCoreApplication.translate("MainWindow", "Apply", None))
        self.checkBox_crop.setText(
            QCoreApplication.translate("MainWindow", "Show crop?", None)
        )
        self.checkBox_annotate.setText(
            QCoreApplication.translate("MainWindow", "Annotate?", None)
        )
        self.FilterTabs.setTabText(
            self.FilterTabs.indexOf(self.tab_7),
            QCoreApplication.translate("MainWindow", "Crop", None),
        )
        self.label_8.setText(
            QCoreApplication.translate("MainWindow", "Hue (0-180)", None)
        )
        self.label_9.setText(
            QCoreApplication.translate("MainWindow", "Saturation (0-255)", None)
        )
        self.label_5.setText(
            QCoreApplication.translate("MainWindow", "Value (0-255)", None)
        )
        self.FilterTabs.setTabText(
            self.FilterTabs.indexOf(self.tab_3),
            QCoreApplication.translate("MainWindow", "Model Filter", None),
        )
        self.label_15.setText(
            QCoreApplication.translate("MainWindow", "Hue (0-180)", None)
        )
        self.label_16.setText(
            QCoreApplication.translate("MainWindow", "Saturation (0-255)", None)
        )
        self.label_6.setText(
            QCoreApplication.translate("MainWindow", "Value (0-255)", None)
        )
        self.FilterTabs.setTabText(
            self.FilterTabs.indexOf(self.tab_4),
            QCoreApplication.translate("MainWindow", "Shock Filter", None),
        )
        self.pushButton_save_frame.setText(
            QCoreApplication.translate("MainWindow", "Save Current Frame", None)
        )
        self.groupBox.setTitle(
            QCoreApplication.translate("MainWindow", "Output parameters", None)
        )
        self.label_17.setText(
            QCoreApplication.translate("MainWindow", "Frame range:", None)
        )
        self.label_10.setText(
            QCoreApplication.translate("MainWindow", "Process every Nth:", None)
        )
        self.label_20.setText(
            QCoreApplication.translate("MainWindow", "Output filename:", None)
        )
        self.checkBox_writeVideo.setText(
            QCoreApplication.translate("MainWindow", "Write video?", None)
        )
        self.pushButton_process.setText(
            QCoreApplication.translate("MainWindow", "Process All", None)
        )
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab),
            QCoreApplication.translate("MainWindow", "Extract Edges", None),
        )
        self.pushButton_LoadFiles.setText(
            QCoreApplication.translate("MainWindow", "Load Files", None)
        )
        self.pushButton_export_csv.setText(
            QCoreApplication.translate("MainWindow", "Export CSV", None)
        )
        self.pushButton_PlotData.setText(
            QCoreApplication.translate("MainWindow", "Plot Data", None)
        )
        self.pushButton_fitData.setText(
            QCoreApplication.translate("MainWindow", "Fit Data", None)
        )
        self.label_11.setText(QCoreApplication.translate("MainWindow", "Units:", None))
        self.comboBox_units.setItemText(
            0, QCoreApplication.translate("MainWindow", "[in]", None)
        )
        self.comboBox_units.setItemText(
            1, QCoreApplication.translate("MainWindow", "[cm]", None)
        )
        self.comboBox_units.setItemText(
            2, QCoreApplication.translate("MainWindow", "[mm]", None)
        )
        self.comboBox_units.setItemText(
            3, QCoreApplication.translate("MainWindow", "pixels", None)
        )

        self.label_18.setText(
            QCoreApplication.translate("MainWindow", "Frames per sec:", None)
        )
        self.label_2.setText(
            QCoreApplication.translate("MainWindow", "Mask nframes:", None)
        )
        self.label_display_shock2.setText(
            QCoreApplication.translate("MainWindow", "Display Shock", None)
        )
        self.checkBox_display_shock2.setText("")
        self.tabWidget_2.setTabText(
            self.tabWidget_2.indexOf(self.tab_5),
            QCoreApplication.translate("MainWindow", "Plotting params", None),
        )
        self.groupBox_3.setTitle(
            QCoreApplication.translate("MainWindow", "Fitting Parameters", None)
        )
        self.label_12.setText(
            QCoreApplication.translate("MainWindow", "Fit type:", None)
        )
        self.comboBox_fit_type.setItemText(
            0, QCoreApplication.translate("MainWindow", "linear", None)
        )

        self.label_13.setText(
            QCoreApplication.translate("MainWindow", "Start time:", None)
        )
        self.label_14.setText(
            QCoreApplication.translate("MainWindow", "End time:", None)
        )
        self.tabWidget_2.setTabText(
            self.tabWidget_2.indexOf(self.tab_6),
            QCoreApplication.translate("MainWindow", "Fitting params", None),
        )
        self.groupBox_XT_params.setTitle(
            QCoreApplication.translate("MainWindow", "Visible Traces on XT plot", None)
        )
        self.checkBox_shock_center.setText(
            QCoreApplication.translate("MainWindow", "Shock center", None)
        )
        self.checkBox_m95_radius.setText(
            QCoreApplication.translate("MainWindow", "-95% radius", None)
        )
        self.checkBox_shockmodel.setText(
            QCoreApplication.translate("MainWindow", "Shock-model dist", None)
        )
        self.checkBox_ypos.setText(
            QCoreApplication.translate("MainWindow", "Model axis-position", None)
        )
        self.checkBox_m50_radius.setText(
            QCoreApplication.translate("MainWindow", "-50% radius", None)
        )
        self.checkBox_shock_area.setText(
            QCoreApplication.translate("MainWindow", "Shock area", None)
        )
        self.checkBox_95_radius.setText(
            QCoreApplication.translate("MainWindow", "+95% radius", None)
        )
        self.checkBox_model_center.setText(
            QCoreApplication.translate("MainWindow", "Model center", None)
        )
        self.checkBox_50_radius.setText(
            QCoreApplication.translate("MainWindow", "+50% radius ", None)
        )
        self.checkBox_model_rad.setText(
            QCoreApplication.translate("MainWindow", "Model radius", None)
        )
        self.groupBox_data_summary.setTitle(
            QCoreApplication.translate("MainWindow", "Data Summary", None)
        )
        self.label_data_summary.setText("")
        self.tabWidget.setTabText(
            self.tabWidget.indexOf(self.tab_2),
            QCoreApplication.translate("MainWindow", "Analyze", None),
        )
        self.basebar.setText("")
        self.menuMenu.setTitle(QCoreApplication.translate("MainWindow", "Menu", None))
        self.toolBar.setWindowTitle(
            QCoreApplication.translate("MainWindow", "toolBar", None)
        )

    # retranslateUi
