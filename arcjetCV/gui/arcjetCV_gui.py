# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'arcjetCV.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QRect, QSize, Qt)
from PySide6.QtGui import (QAction)
from PySide6.QtWidgets import (QCheckBox, QComboBox, QDoubleSpinBox,
    QFormLayout, QGridLayout, QGroupBox, QHBoxLayout,
    QLabel, QLayout, QLineEdit, QListView,
    QMenu, QMenuBar, QPushButton,
    QSizePolicy, QSpacerItem, QSpinBox, QStatusBar,
    QTabWidget, QTextBrowser, QToolBar, QVBoxLayout,
    QWidget)
from arcjetCV.gui.custom_classes import MatplotlibWidget

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1175, 824)
        self.actionLoad_video = QAction(MainWindow)
        self.actionLoad_video.setObjectName(u"actionLoad_video")
        self.actionExit = QAction(MainWindow)
        self.actionExit.setObjectName(u"actionExit")
        self.actionSave_Filter = QAction(MainWindow)
        self.actionSave_Filter.setObjectName(u"actionSave_Filter")
        self.actionLoad_Filter_2 = QAction(MainWindow)
        self.actionLoad_Filter_2.setObjectName(u"actionLoad_Filter_2")
        self.actionSave_Filter_2 = QAction(MainWindow)
        self.actionSave_Filter_2.setObjectName(u"actionSave_Filter_2")
        self.actionExit_2 = QAction(MainWindow)
        self.actionExit_2.setObjectName(u"actionExit_2")
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout_4 = QVBoxLayout(self.centralwidget)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName(u"tabWidget")
        self.tab_8 = QWidget()
        self.tab_8.setObjectName(u"tab_8")
        self.gridLayout_4 = QGridLayout(self.tab_8)
        self.gridLayout_4.setObjectName(u"gridLayout_4")
        self.listView_calibration_imgs = QListView(self.tab_8)
        self.listView_calibration_imgs.setObjectName(u"listView_calibration_imgs")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.listView_calibration_imgs.sizePolicy().hasHeightForWidth())
        self.listView_calibration_imgs.setSizePolicy(sizePolicy)

        self.gridLayout_4.addWidget(self.listView_calibration_imgs, 5, 1, 1, 1)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.gridLayout_4.addItem(self.verticalSpacer_9, 4, 2, 1, 1)

        self.Window_view_img = MatplotlibWidget(self.tab_8)
        self.Window_view_img.setObjectName(u"Window_view_img")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.Window_view_img.sizePolicy().hasHeightForWidth())
        self.Window_view_img.setSizePolicy(sizePolicy1)
        self.Window_view_img.setMinimumSize(QSize(741, 200))

        self.gridLayout_4.addWidget(self.Window_view_img, 0, 1, 5, 1)

        self.textBrowser_calibration_values = QTextBrowser(self.tab_8)
        self.textBrowser_calibration_values.setObjectName(u"textBrowser_calibration_values")

        self.gridLayout_4.addWidget(self.textBrowser_calibration_values, 5, 2, 1, 1)

        self.groupBox_4 = QGroupBox(self.tab_8)
        self.groupBox_4.setObjectName(u"groupBox_4")
        self.groupBox_4.setMinimumSize(QSize(300, 0))
        self.gridLayout_9 = QGridLayout(self.groupBox_4)
        self.gridLayout_9.setObjectName(u"gridLayout_9")
        self.label_23 = QLabel(self.groupBox_4)
        self.label_23.setObjectName(u"label_23")

        self.gridLayout_9.addWidget(self.label_23, 4, 0, 1, 2)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.gridLayout_9.addItem(self.horizontalSpacer_2, 1, 5, 1, 1)

        self.spinBox_pattern_ny = QSpinBox(self.groupBox_4)
        self.spinBox_pattern_ny.setObjectName(u"spinBox_pattern_ny")
        self.spinBox_pattern_ny.setValue(9)

        self.gridLayout_9.addWidget(self.spinBox_pattern_ny, 1, 4, 1, 1)

        self.label_diag_len = QLabel(self.groupBox_4)
        self.label_diag_len.setObjectName(u"label_diag_len")

        self.gridLayout_9.addWidget(self.label_diag_len, 2, 0, 1, 2)

        self.label_24 = QLabel(self.groupBox_4)
        self.label_24.setObjectName(u"label_24")

        self.gridLayout_9.addWidget(self.label_24, 3, 0, 1, 2)

        self.spinBox_pattern_nx = QSpinBox(self.groupBox_4)
        self.spinBox_pattern_nx.setObjectName(u"spinBox_pattern_nx")
        self.spinBox_pattern_nx.setValue(4)

        self.gridLayout_9.addWidget(self.spinBox_pattern_nx, 1, 2, 1, 1)

        self.label_pattern_nxm = QLabel(self.groupBox_4)
        self.label_pattern_nxm.setObjectName(u"label_pattern_nxm")

        self.gridLayout_9.addWidget(self.label_pattern_nxm, 1, 0, 1, 2)

        self.label_26 = QLabel(self.groupBox_4)
        self.label_26.setObjectName(u"label_26")

        self.gridLayout_9.addWidget(self.label_26, 1, 3, 1, 1)

        self.label_pattern_type = QLabel(self.groupBox_4)
        self.label_pattern_type.setObjectName(u"label_pattern_type")

        self.gridLayout_9.addWidget(self.label_pattern_type, 0, 0, 1, 1)

        self.comboBox_pattern_type = QComboBox(self.groupBox_4)
        self.comboBox_pattern_type.addItem("")
        self.comboBox_pattern_type.addItem("")
        self.comboBox_pattern_type.setObjectName(u"comboBox_pattern_type")

        self.gridLayout_9.addWidget(self.comboBox_pattern_type, 0, 1, 1, 5)

        self.doubleSpinBox_diag_len = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox_diag_len.setObjectName(u"doubleSpinBox_diag_len")

        self.gridLayout_9.addWidget(self.doubleSpinBox_diag_len, 2, 2, 1, 4)

        self.comboBox = QComboBox(self.groupBox_4)
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.setObjectName(u"comboBox")

        self.gridLayout_9.addWidget(self.comboBox, 3, 2, 1, 4)

        self.doubleSpinBox = QDoubleSpinBox(self.groupBox_4)
        self.doubleSpinBox.setObjectName(u"doubleSpinBox")

        self.gridLayout_9.addWidget(self.doubleSpinBox, 4, 2, 1, 4)

        self.pushButton_save_calib = QPushButton(self.groupBox_4)
        self.pushButton_save_calib.setObjectName(u"pushButton_save_calib")

        self.gridLayout_9.addWidget(self.pushButton_save_calib, 6, 0, 1, 6)


        self.gridLayout_4.addWidget(self.groupBox_4, 3, 2, 1, 1)

        self.groupBox_5 = QGroupBox(self.tab_8)
        self.groupBox_5.setObjectName(u"groupBox_5")
        self.gridLayout_10 = QGridLayout(self.groupBox_5)
        self.gridLayout_10.setObjectName(u"gridLayout_10")
        self.pushButton = QPushButton(self.groupBox_5)
        self.pushButton.setObjectName(u"pushButton")

        self.gridLayout_10.addWidget(self.pushButton, 0, 0, 1, 1)

        self.pushButton_2 = QPushButton(self.groupBox_5)
        self.pushButton_2.setObjectName(u"pushButton_2")

        self.gridLayout_10.addWidget(self.pushButton_2, 1, 0, 1, 1)


        self.gridLayout_4.addWidget(self.groupBox_5, 0, 2, 2, 1)

        self.tabWidget.addTab(self.tab_8, "")
        self.tab = QWidget()
        self.tab.setObjectName(u"tab")
        self.horizontalLayout_8 = QHBoxLayout(self.tab)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.Window0 = MatplotlibWidget(self.tab)
        self.Window0.setObjectName(u"Window0")
        sizePolicy1.setHeightForWidth(self.Window0.sizePolicy().hasHeightForWidth())
        self.Window0.setSizePolicy(sizePolicy1)
        self.Window0.setMinimumSize(QSize(731, 451))

        self.verticalLayout.addWidget(self.Window0)

        self.Window3 = MatplotlibWidget(self.tab)
        self.Window3.setObjectName(u"Window3")
        sizePolicy1.setHeightForWidth(self.Window3.sizePolicy().hasHeightForWidth())
        self.Window3.setSizePolicy(sizePolicy1)
        self.Window3.setMinimumSize(QSize(731, 100))
        self.Window3.setMaximumSize(QSize(16777215, 300))

        self.verticalLayout.addWidget(self.Window3)


        self.horizontalLayout_8.addLayout(self.verticalLayout)

        self.verticalLayout_6 = QVBoxLayout()
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.pushButton_loadVideo = QPushButton(self.tab)
        self.pushButton_loadVideo.setObjectName(u"pushButton_loadVideo")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.pushButton_loadVideo.sizePolicy().hasHeightForWidth())
        self.pushButton_loadVideo.setSizePolicy(sizePolicy2)

        self.verticalLayout_6.addWidget(self.pushButton_loadVideo)

        self.verticalSpacer_4 = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_6.addItem(self.verticalSpacer_4)

        self.groupBox_2 = QGroupBox(self.tab)
        self.groupBox_2.setObjectName(u"groupBox_2")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Minimum)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy3)
        self.groupBox_2.setMinimumSize(QSize(350, 0))
        self.verticalLayout_5 = QVBoxLayout(self.groupBox_2)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.gridLayout_6 = QGridLayout()
        self.gridLayout_6.setObjectName(u"gridLayout_6")
        self.label_3 = QLabel(self.groupBox_2)
        self.label_3.setObjectName(u"label_3")

        self.gridLayout_6.addWidget(self.label_3, 1, 0, 1, 1)

        self.label_4 = QLabel(self.groupBox_2)
        self.label_4.setObjectName(u"label_4")

        self.gridLayout_6.addWidget(self.label_4, 2, 0, 1, 1)

        self.spinBox_FrameIndex = QSpinBox(self.groupBox_2)
        self.spinBox_FrameIndex.setObjectName(u"spinBox_FrameIndex")
        sizePolicy2.setHeightForWidth(self.spinBox_FrameIndex.sizePolicy().hasHeightForWidth())
        self.spinBox_FrameIndex.setSizePolicy(sizePolicy2)
        self.spinBox_FrameIndex.setMaximum(100000)
        self.spinBox_FrameIndex.setValue(0)

        self.gridLayout_6.addWidget(self.spinBox_FrameIndex, 0, 1, 1, 1)

        self.label_display_shock = QLabel(self.groupBox_2)
        self.label_display_shock.setObjectName(u"label_display_shock")

        self.gridLayout_6.addWidget(self.label_display_shock, 3, 0, 1, 1)

        self.comboBox_flowDirection = QComboBox(self.groupBox_2)
        self.comboBox_flowDirection.addItem("")
        self.comboBox_flowDirection.addItem("")
        self.comboBox_flowDirection.setObjectName(u"comboBox_flowDirection")
        sizePolicy2.setHeightForWidth(self.comboBox_flowDirection.sizePolicy().hasHeightForWidth())
        self.comboBox_flowDirection.setSizePolicy(sizePolicy2)

        self.gridLayout_6.addWidget(self.comboBox_flowDirection, 1, 1, 1, 1)

        self.checkBox_display_shock = QCheckBox(self.groupBox_2)
        self.checkBox_display_shock.setObjectName(u"checkBox_display_shock")
        self.checkBox_display_shock.setChecked(True)

        self.gridLayout_6.addWidget(self.checkBox_display_shock, 3, 1, 1, 1)

        self.label_7 = QLabel(self.groupBox_2)
        self.label_7.setObjectName(u"label_7")

        self.gridLayout_6.addWidget(self.label_7, 0, 0, 1, 1)

        self.comboBox_filterType = QComboBox(self.groupBox_2)
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.addItem("")
        self.comboBox_filterType.setObjectName(u"comboBox_filterType")
        sizePolicy2.setHeightForWidth(self.comboBox_filterType.sizePolicy().hasHeightForWidth())
        self.comboBox_filterType.setSizePolicy(sizePolicy2)

        self.gridLayout_6.addWidget(self.comboBox_filterType, 2, 1, 1, 1)


        self.verticalLayout_5.addLayout(self.gridLayout_6)

        self.verticalSpacer_5 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_5.addItem(self.verticalSpacer_5)

        self.FilterTabs = QTabWidget(self.groupBox_2)
        self.FilterTabs.setObjectName(u"FilterTabs")
        sizePolicy.setHeightForWidth(self.FilterTabs.sizePolicy().hasHeightForWidth())
        self.FilterTabs.setSizePolicy(sizePolicy)
        self.tab_7 = QWidget()
        self.tab_7.setObjectName(u"tab_7")
        self.layoutWidget_2 = QWidget(self.tab_7)
        self.layoutWidget_2.setObjectName(u"layoutWidget_2")
        self.layoutWidget_2.setGeometry(QRect(0, 10, 311, 101))
        self.formLayout_8 = QFormLayout(self.layoutWidget_2)
        self.formLayout_8.setObjectName(u"formLayout_8")
        self.formLayout_8.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout_8.setLabelAlignment(Qt.AlignRight|Qt.AlignTrailing|Qt.AlignVCenter)
        self.formLayout_8.setContentsMargins(0, 0, 0, 0)
        self.label_19 = QLabel(self.layoutWidget_2)
        self.label_19.setObjectName(u"label_19")

        self.formLayout_8.setWidget(0, QFormLayout.LabelRole, self.label_19)

        self.horizontalLayout_18 = QHBoxLayout()
        self.horizontalLayout_18.setObjectName(u"horizontalLayout_18")
        self.spinBox_crop_xmax = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_xmax.setObjectName(u"spinBox_crop_xmax")
        self.spinBox_crop_xmax.setMaximum(10000)
        self.spinBox_crop_xmax.setValue(20)

        self.horizontalLayout_18.addWidget(self.spinBox_crop_xmax)

        self.spinBox_crop_xmin = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_xmin.setObjectName(u"spinBox_crop_xmin")
        self.spinBox_crop_xmin.setMaximum(10000)
        self.spinBox_crop_xmin.setValue(20)

        self.horizontalLayout_18.addWidget(self.spinBox_crop_xmin)


        self.formLayout_8.setLayout(0, QFormLayout.FieldRole, self.horizontalLayout_18)

        self.label_21 = QLabel(self.layoutWidget_2)
        self.label_21.setObjectName(u"label_21")

        self.formLayout_8.setWidget(1, QFormLayout.LabelRole, self.label_21)

        self.applyCrop = QPushButton(self.layoutWidget_2)
        self.applyCrop.setObjectName(u"applyCrop")

        self.formLayout_8.setWidget(2, QFormLayout.LabelRole, self.applyCrop)

        self.horizontalLayout_20 = QHBoxLayout()
        self.horizontalLayout_20.setObjectName(u"horizontalLayout_20")
        self.checkBox_crop = QCheckBox(self.layoutWidget_2)
        self.checkBox_crop.setObjectName(u"checkBox_crop")
        self.checkBox_crop.setChecked(True)
        self.checkBox_crop.setTristate(False)

        self.horizontalLayout_20.addWidget(self.checkBox_crop)

        self.checkBox_annotate = QCheckBox(self.layoutWidget_2)
        self.checkBox_annotate.setObjectName(u"checkBox_annotate")
        self.checkBox_annotate.setChecked(True)

        self.horizontalLayout_20.addWidget(self.checkBox_annotate)


        self.formLayout_8.setLayout(2, QFormLayout.FieldRole, self.horizontalLayout_20)

        self.horizontalLayout_19 = QHBoxLayout()
        self.horizontalLayout_19.setObjectName(u"horizontalLayout_19")
        self.spinBox_crop_ymax = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_ymax.setObjectName(u"spinBox_crop_ymax")
        self.spinBox_crop_ymax.setMaximum(10000)
        self.spinBox_crop_ymax.setValue(100)

        self.horizontalLayout_19.addWidget(self.spinBox_crop_ymax)

        self.spinBox_crop_ymin = QSpinBox(self.layoutWidget_2)
        self.spinBox_crop_ymin.setObjectName(u"spinBox_crop_ymin")
        self.spinBox_crop_ymin.setMaximum(10000)
        self.spinBox_crop_ymin.setValue(100)

        self.horizontalLayout_19.addWidget(self.spinBox_crop_ymin)


        self.formLayout_8.setLayout(1, QFormLayout.FieldRole, self.horizontalLayout_19)

        self.FilterTabs.addTab(self.tab_7, "")
        self.tab_3 = QWidget()
        self.tab_3.setObjectName(u"tab_3")
        self.verticalLayout_2 = QVBoxLayout(self.tab_3)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.gridLayout_8 = QGridLayout()
        self.gridLayout_8.setObjectName(u"gridLayout_8")
        self.label_8 = QLabel(self.tab_3)
        self.label_8.setObjectName(u"label_8")

        self.gridLayout_8.addWidget(self.label_8, 0, 0, 1, 1)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.minHue = QSpinBox(self.tab_3)
        self.minHue.setObjectName(u"minHue")
        self.minHue.setMaximum(180)
        self.minHue.setValue(0)

        self.horizontalLayout_3.addWidget(self.minHue)

        self.maxHue = QSpinBox(self.tab_3)
        self.maxHue.setObjectName(u"maxHue")
        self.maxHue.setMaximum(180)
        self.maxHue.setValue(121)

        self.horizontalLayout_3.addWidget(self.maxHue)


        self.gridLayout_8.addLayout(self.horizontalLayout_3, 0, 1, 1, 1)

        self.label_9 = QLabel(self.tab_3)
        self.label_9.setObjectName(u"label_9")

        self.gridLayout_8.addWidget(self.label_9, 1, 0, 1, 1)

        self.horizontalLayout_4 = QHBoxLayout()
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.minSaturation = QSpinBox(self.tab_3)
        self.minSaturation.setObjectName(u"minSaturation")
        self.minSaturation.setMaximum(255)
        self.minSaturation.setValue(0)

        self.horizontalLayout_4.addWidget(self.minSaturation)

        self.maxSaturation = QSpinBox(self.tab_3)
        self.maxSaturation.setObjectName(u"maxSaturation")
        self.maxSaturation.setMaximum(255)
        self.maxSaturation.setValue(125)

        self.horizontalLayout_4.addWidget(self.maxSaturation)


        self.gridLayout_8.addLayout(self.horizontalLayout_4, 1, 1, 1, 1)

        self.label_5 = QLabel(self.tab_3)
        self.label_5.setObjectName(u"label_5")

        self.gridLayout_8.addWidget(self.label_5, 2, 0, 1, 1)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.minIntensity = QSpinBox(self.tab_3)
        self.minIntensity.setObjectName(u"minIntensity")
        self.minIntensity.setMaximum(254)
        self.minIntensity.setValue(150)

        self.horizontalLayout_2.addWidget(self.minIntensity)

        self.maxIntensity = QSpinBox(self.tab_3)
        self.maxIntensity.setObjectName(u"maxIntensity")
        self.maxIntensity.setMaximum(255)
        self.maxIntensity.setValue(255)

        self.horizontalLayout_2.addWidget(self.maxIntensity)


        self.gridLayout_8.addLayout(self.horizontalLayout_2, 2, 1, 1, 1)


        self.verticalLayout_2.addLayout(self.gridLayout_8)

        self.FilterTabs.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.tab_4.setObjectName(u"tab_4")
        self.horizontalLayout_9 = QHBoxLayout(self.tab_4)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.gridLayout_7 = QGridLayout()
        self.gridLayout_7.setObjectName(u"gridLayout_7")
        self.label_15 = QLabel(self.tab_4)
        self.label_15.setObjectName(u"label_15")

        self.gridLayout_7.addWidget(self.label_15, 0, 0, 1, 1)

        self.horizontalLayout_6 = QHBoxLayout()
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.minHue_2 = QSpinBox(self.tab_4)
        self.minHue_2.setObjectName(u"minHue_2")
        self.minHue_2.setMaximum(180)
        self.minHue_2.setValue(125)

        self.horizontalLayout_6.addWidget(self.minHue_2)

        self.maxHue_2 = QSpinBox(self.tab_4)
        self.maxHue_2.setObjectName(u"maxHue_2")
        self.maxHue_2.setMaximum(180)
        self.maxHue_2.setValue(170)

        self.horizontalLayout_6.addWidget(self.maxHue_2)


        self.gridLayout_7.addLayout(self.horizontalLayout_6, 0, 1, 1, 1)

        self.label_16 = QLabel(self.tab_4)
        self.label_16.setObjectName(u"label_16")

        self.gridLayout_7.addWidget(self.label_16, 1, 0, 1, 1)

        self.horizontalLayout_7 = QHBoxLayout()
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.minSaturation_2 = QSpinBox(self.tab_4)
        self.minSaturation_2.setObjectName(u"minSaturation_2")
        self.minSaturation_2.setMaximum(255)
        self.minSaturation_2.setValue(40)

        self.horizontalLayout_7.addWidget(self.minSaturation_2)

        self.maxSaturation_2 = QSpinBox(self.tab_4)
        self.maxSaturation_2.setObjectName(u"maxSaturation_2")
        self.maxSaturation_2.setMaximum(255)
        self.maxSaturation_2.setValue(80)

        self.horizontalLayout_7.addWidget(self.maxSaturation_2)


        self.gridLayout_7.addLayout(self.horizontalLayout_7, 1, 1, 1, 1)

        self.label_6 = QLabel(self.tab_4)
        self.label_6.setObjectName(u"label_6")

        self.gridLayout_7.addWidget(self.label_6, 2, 0, 1, 1)

        self.horizontalLayout_5 = QHBoxLayout()
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.minIntensity_2 = QSpinBox(self.tab_4)
        self.minIntensity_2.setObjectName(u"minIntensity_2")
        self.minIntensity_2.setMaximum(254)
        self.minIntensity_2.setValue(85)

        self.horizontalLayout_5.addWidget(self.minIntensity_2)

        self.maxIntensity_2 = QSpinBox(self.tab_4)
        self.maxIntensity_2.setObjectName(u"maxIntensity_2")
        self.maxIntensity_2.setMaximum(255)
        self.maxIntensity_2.setValue(230)

        self.horizontalLayout_5.addWidget(self.maxIntensity_2)


        self.gridLayout_7.addLayout(self.horizontalLayout_5, 2, 1, 1, 1)


        self.horizontalLayout_9.addLayout(self.gridLayout_7)

        self.FilterTabs.addTab(self.tab_4, "")

        self.verticalLayout_5.addWidget(self.FilterTabs)


        self.verticalLayout_6.addWidget(self.groupBox_2)

        self.pushButton_save_frame = QPushButton(self.tab)
        self.pushButton_save_frame.setObjectName(u"pushButton_save_frame")

        self.verticalLayout_6.addWidget(self.pushButton_save_frame)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer)

        self.groupBox = QGroupBox(self.tab)
        self.groupBox.setObjectName(u"groupBox")
        sizePolicy.setHeightForWidth(self.groupBox.sizePolicy().hasHeightForWidth())
        self.groupBox.setSizePolicy(sizePolicy)
        self.verticalLayout_3 = QVBoxLayout(self.groupBox)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.gridLayout_5 = QGridLayout()
        self.gridLayout_5.setObjectName(u"gridLayout_5")
        self.label_17 = QLabel(self.groupBox)
        self.label_17.setObjectName(u"label_17")

        self.gridLayout_5.addWidget(self.label_17, 0, 0, 1, 1)

        self.horizontalLayout_10 = QHBoxLayout()
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.spinBox_FirstGoodFrame = QSpinBox(self.groupBox)
        self.spinBox_FirstGoodFrame.setObjectName(u"spinBox_FirstGoodFrame")
        self.spinBox_FirstGoodFrame.setMaximum(100000)
        self.spinBox_FirstGoodFrame.setValue(0)

        self.horizontalLayout_10.addWidget(self.spinBox_FirstGoodFrame)

        self.spinBox_LastGoodFrame = QSpinBox(self.groupBox)
        self.spinBox_LastGoodFrame.setObjectName(u"spinBox_LastGoodFrame")
        self.spinBox_LastGoodFrame.setMaximum(100000)
        self.spinBox_LastGoodFrame.setValue(0)

        self.horizontalLayout_10.addWidget(self.spinBox_LastGoodFrame)


        self.gridLayout_5.addLayout(self.horizontalLayout_10, 0, 1, 1, 1)

        self.label_10 = QLabel(self.groupBox)
        self.label_10.setObjectName(u"label_10")

        self.gridLayout_5.addWidget(self.label_10, 1, 0, 1, 1)

        self.spinBox_frame_skips = QSpinBox(self.groupBox)
        self.spinBox_frame_skips.setObjectName(u"spinBox_frame_skips")
        self.spinBox_frame_skips.setMinimum(1)
        self.spinBox_frame_skips.setMaximum(200)
        self.spinBox_frame_skips.setValue(5)

        self.gridLayout_5.addWidget(self.spinBox_frame_skips, 1, 1, 1, 1)

        self.label_20 = QLabel(self.groupBox)
        self.label_20.setObjectName(u"label_20")

        self.gridLayout_5.addWidget(self.label_20, 2, 0, 1, 1)

        self.lineEdit_filename = QLineEdit(self.groupBox)
        self.lineEdit_filename.setObjectName(u"lineEdit_filename")
        sizePolicy2.setHeightForWidth(self.lineEdit_filename.sizePolicy().hasHeightForWidth())
        self.lineEdit_filename.setSizePolicy(sizePolicy2)

        self.gridLayout_5.addWidget(self.lineEdit_filename, 2, 1, 1, 1)


        self.verticalLayout_3.addLayout(self.gridLayout_5)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.checkBox_writeVideo = QCheckBox(self.groupBox)
        self.checkBox_writeVideo.setObjectName(u"checkBox_writeVideo")

        self.horizontalLayout.addWidget(self.checkBox_writeVideo)

        self.pushButton_process = QPushButton(self.groupBox)
        self.pushButton_process.setObjectName(u"pushButton_process")

        self.horizontalLayout.addWidget(self.pushButton_process)


        self.verticalLayout_3.addLayout(self.horizontalLayout)


        self.verticalLayout_6.addWidget(self.groupBox)

        self.horizontalSpacer_test = QSpacerItem(40, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout_6.addItem(self.horizontalSpacer_test)


        self.horizontalLayout_8.addLayout(self.verticalLayout_6)

        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QWidget()
        self.tab_2.setObjectName(u"tab_2")
        self.horizontalLayout_11 = QHBoxLayout(self.tab_2)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.verticalLayout_8 = QVBoxLayout()
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.horizontalLayout_12 = QHBoxLayout()
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setSizeConstraint(QLayout.SetMaximumSize)
        self.Window1 = MatplotlibWidget(self.tab_2)
        self.Window1.setObjectName(u"Window1")
        sizePolicy1.setHeightForWidth(self.Window1.sizePolicy().hasHeightForWidth())
        self.Window1.setSizePolicy(sizePolicy1)
        self.Window1.setMinimumSize(QSize(400, 350))

        self.horizontalLayout_12.addWidget(self.Window1)

        self.Window2 = MatplotlibWidget(self.tab_2)
        self.Window2.setObjectName(u"Window2")
        sizePolicy1.setHeightForWidth(self.Window2.sizePolicy().hasHeightForWidth())
        self.Window2.setSizePolicy(sizePolicy1)
        self.Window2.setMinimumSize(QSize(400, 350))

        self.horizontalLayout_12.addWidget(self.Window2)


        self.verticalLayout_8.addLayout(self.horizontalLayout_12)

        self.textBrowser = QTextBrowser(self.tab_2)
        self.textBrowser.setObjectName(u"textBrowser")
        sizePolicy1.setHeightForWidth(self.textBrowser.sizePolicy().hasHeightForWidth())
        self.textBrowser.setSizePolicy(sizePolicy1)
        self.textBrowser.setMaximumSize(QSize(16777215, 250))

        self.verticalLayout_8.addWidget(self.textBrowser)


        self.horizontalLayout_11.addLayout(self.verticalLayout_8)

        self.verticalLayout_7 = QVBoxLayout()
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.horizontalLayout_13 = QHBoxLayout()
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.pushButton_LoadFiles = QPushButton(self.tab_2)
        self.pushButton_LoadFiles.setObjectName(u"pushButton_LoadFiles")

        self.horizontalLayout_13.addWidget(self.pushButton_LoadFiles)

        self.pushButton_export_csv = QPushButton(self.tab_2)
        self.pushButton_export_csv.setObjectName(u"pushButton_export_csv")

        self.horizontalLayout_13.addWidget(self.pushButton_export_csv)


        self.verticalLayout_7.addLayout(self.horizontalLayout_13)

        self.horizontalLayout_15 = QHBoxLayout()
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.pushButton_PlotData = QPushButton(self.tab_2)
        self.pushButton_PlotData.setObjectName(u"pushButton_PlotData")

        self.horizontalLayout_15.addWidget(self.pushButton_PlotData)

        self.pushButton_fitData = QPushButton(self.tab_2)
        self.pushButton_fitData.setObjectName(u"pushButton_fitData")

        self.horizontalLayout_15.addWidget(self.pushButton_fitData)


        self.verticalLayout_7.addLayout(self.horizontalLayout_15)

        self.verticalSpacer_6 = QSpacerItem(20, 15, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_7.addItem(self.verticalSpacer_6)

        self.tabWidget_2 = QTabWidget(self.tab_2)
        self.tabWidget_2.setObjectName(u"tabWidget_2")
        sizePolicy.setHeightForWidth(self.tabWidget_2.sizePolicy().hasHeightForWidth())
        self.tabWidget_2.setSizePolicy(sizePolicy)
        self.tab_5 = QWidget()
        self.tab_5.setObjectName(u"tab_5")
        self.gridLayout_2 = QGridLayout(self.tab_5)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.label = QLabel(self.tab_5)
        self.label.setObjectName(u"label")

        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)

        self.doubleSpinBox_diameter = QDoubleSpinBox(self.tab_5)
        self.doubleSpinBox_diameter.setObjectName(u"doubleSpinBox_diameter")
        self.doubleSpinBox_diameter.setMinimum(0.100000000000000)
        self.doubleSpinBox_diameter.setMaximum(1000.000000000000000)
        self.doubleSpinBox_diameter.setValue(101.599999999999994)

        self.gridLayout_2.addWidget(self.doubleSpinBox_diameter, 0, 1, 1, 1)

        self.label_11 = QLabel(self.tab_5)
        self.label_11.setObjectName(u"label_11")

        self.gridLayout_2.addWidget(self.label_11, 1, 0, 1, 1)

        self.comboBox_units = QComboBox(self.tab_5)
        self.comboBox_units.addItem("")
        self.comboBox_units.addItem("")
        self.comboBox_units.addItem("")
        self.comboBox_units.addItem("")
        self.comboBox_units.setObjectName(u"comboBox_units")

        self.gridLayout_2.addWidget(self.comboBox_units, 1, 1, 1, 1)

        self.label_18 = QLabel(self.tab_5)
        self.label_18.setObjectName(u"label_18")

        self.gridLayout_2.addWidget(self.label_18, 2, 0, 1, 1)

        self.doubleSpinBox_fps = QDoubleSpinBox(self.tab_5)
        self.doubleSpinBox_fps.setObjectName(u"doubleSpinBox_fps")
        self.doubleSpinBox_fps.setMinimum(1.000000000000000)
        self.doubleSpinBox_fps.setMaximum(120.000000000000000)
        self.doubleSpinBox_fps.setValue(30.000000000000000)

        self.gridLayout_2.addWidget(self.doubleSpinBox_fps, 2, 1, 1, 1)

        self.label_2 = QLabel(self.tab_5)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMaximumSize(QSize(100, 30))

        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)

        self.spinBox_mask_frames = QSpinBox(self.tab_5)
        self.spinBox_mask_frames.setObjectName(u"spinBox_mask_frames")
        self.spinBox_mask_frames.setMinimumSize(QSize(0, 0))
        self.spinBox_mask_frames.setMaximumSize(QSize(150, 30))
        self.spinBox_mask_frames.setMinimum(1)
        self.spinBox_mask_frames.setMaximum(1000)
        self.spinBox_mask_frames.setValue(10)

        self.gridLayout_2.addWidget(self.spinBox_mask_frames, 3, 1, 1, 1)

        self.label_display_shock2 = QLabel(self.tab_5)
        self.label_display_shock2.setObjectName(u"label_display_shock2")

        self.gridLayout_2.addWidget(self.label_display_shock2, 4, 0, 1, 1)

        self.checkBox_display_shock2 = QCheckBox(self.tab_5)
        self.checkBox_display_shock2.setObjectName(u"checkBox_display_shock2")
        self.checkBox_display_shock2.setChecked(True)

        self.gridLayout_2.addWidget(self.checkBox_display_shock2, 4, 1, 1, 1)

        self.tabWidget_2.addTab(self.tab_5, "")
        self.tab_6 = QWidget()
        self.tab_6.setObjectName(u"tab_6")
        self.verticalLayout_10 = QVBoxLayout(self.tab_6)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.groupBox_3 = QGroupBox(self.tab_6)
        self.groupBox_3.setObjectName(u"groupBox_3")
        self.gridLayout_3 = QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName(u"gridLayout_3")
        self.label_12 = QLabel(self.groupBox_3)
        self.label_12.setObjectName(u"label_12")

        self.gridLayout_3.addWidget(self.label_12, 0, 0, 1, 1)

        self.comboBox_fit_type = QComboBox(self.groupBox_3)
        self.comboBox_fit_type.addItem("")
        self.comboBox_fit_type.setObjectName(u"comboBox_fit_type")

        self.gridLayout_3.addWidget(self.comboBox_fit_type, 0, 1, 1, 1)

        self.label_13 = QLabel(self.groupBox_3)
        self.label_13.setObjectName(u"label_13")

        self.gridLayout_3.addWidget(self.label_13, 1, 0, 1, 1)

        self.doubleSpinBox_fit_start_time = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_fit_start_time.setObjectName(u"doubleSpinBox_fit_start_time")

        self.gridLayout_3.addWidget(self.doubleSpinBox_fit_start_time, 1, 1, 1, 1)

        self.label_14 = QLabel(self.groupBox_3)
        self.label_14.setObjectName(u"label_14")

        self.gridLayout_3.addWidget(self.label_14, 2, 0, 1, 1)

        self.doubleSpinBox_fit_last_time = QDoubleSpinBox(self.groupBox_3)
        self.doubleSpinBox_fit_last_time.setObjectName(u"doubleSpinBox_fit_last_time")

        self.gridLayout_3.addWidget(self.doubleSpinBox_fit_last_time, 2, 1, 1, 1)


        self.verticalLayout_10.addWidget(self.groupBox_3)

        self.tabWidget_2.addTab(self.tab_6, "")

        self.verticalLayout_7.addWidget(self.tabWidget_2)

        self.verticalSpacer_7 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_7.addItem(self.verticalSpacer_7)

        self.groupBox_XT_params = QGroupBox(self.tab_2)
        self.groupBox_XT_params.setObjectName(u"groupBox_XT_params")
        self.gridLayout = QGridLayout(self.groupBox_XT_params)
        self.gridLayout.setObjectName(u"gridLayout")
        self.checkBox_shock_center = QCheckBox(self.groupBox_XT_params)
        self.checkBox_shock_center.setObjectName(u"checkBox_shock_center")

        self.gridLayout.addWidget(self.checkBox_shock_center, 2, 1, 1, 1)

        self.checkBox_m95_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_m95_radius.setObjectName(u"checkBox_m95_radius")
        self.checkBox_m95_radius.setChecked(False)
        self.checkBox_m95_radius.setTristate(False)

        self.gridLayout.addWidget(self.checkBox_m95_radius, 0, 0, 1, 1)

        self.checkBox_shockmodel = QCheckBox(self.groupBox_XT_params)
        self.checkBox_shockmodel.setObjectName(u"checkBox_shockmodel")

        self.gridLayout.addWidget(self.checkBox_shockmodel, 3, 1, 1, 1)

        self.checkBox_ypos = QCheckBox(self.groupBox_XT_params)
        self.checkBox_ypos.setObjectName(u"checkBox_ypos")

        self.gridLayout.addWidget(self.checkBox_ypos, 4, 1, 1, 1)

        self.checkBox_m50_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_m50_radius.setObjectName(u"checkBox_m50_radius")
        self.checkBox_m50_radius.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_m50_radius, 1, 0, 1, 1)

        self.checkBox_shock_area = QCheckBox(self.groupBox_XT_params)
        self.checkBox_shock_area.setObjectName(u"checkBox_shock_area")

        self.gridLayout.addWidget(self.checkBox_shock_area, 0, 1, 1, 1)

        self.checkBox_95_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_95_radius.setObjectName(u"checkBox_95_radius")
        self.checkBox_95_radius.setChecked(False)

        self.gridLayout.addWidget(self.checkBox_95_radius, 4, 0, 1, 1)

        self.checkBox_model_center = QCheckBox(self.groupBox_XT_params)
        self.checkBox_model_center.setObjectName(u"checkBox_model_center")
        self.checkBox_model_center.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_model_center, 2, 0, 1, 1)

        self.checkBox_50_radius = QCheckBox(self.groupBox_XT_params)
        self.checkBox_50_radius.setObjectName(u"checkBox_50_radius")
        self.checkBox_50_radius.setChecked(True)

        self.gridLayout.addWidget(self.checkBox_50_radius, 3, 0, 1, 1)

        self.checkBox_model_rad = QCheckBox(self.groupBox_XT_params)
        self.checkBox_model_rad.setObjectName(u"checkBox_model_rad")

        self.gridLayout.addWidget(self.checkBox_model_rad, 1, 1, 1, 1)


        self.verticalLayout_7.addWidget(self.groupBox_XT_params)

        self.verticalSpacer_8 = QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_7.addItem(self.verticalSpacer_8)

        self.groupBox_data_summary = QGroupBox(self.tab_2)
        self.groupBox_data_summary.setObjectName(u"groupBox_data_summary")
        self.verticalLayout_9 = QVBoxLayout(self.groupBox_data_summary)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.label_data_summary = QLabel(self.groupBox_data_summary)
        self.label_data_summary.setObjectName(u"label_data_summary")

        self.verticalLayout_9.addWidget(self.label_data_summary)


        self.verticalLayout_7.addWidget(self.groupBox_data_summary)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_7.addItem(self.verticalSpacer_2)


        self.horizontalLayout_11.addLayout(self.verticalLayout_7)

        self.tabWidget.addTab(self.tab_2, "")

        self.verticalLayout_4.addWidget(self.tabWidget)

        self.basebar = QLabel(self.centralwidget)
        self.basebar.setObjectName(u"basebar")

        self.verticalLayout_4.addWidget(self.basebar)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 1175, 24))
        self.menuMenu = QMenu(self.menubar)
        self.menuMenu.setObjectName(u"menuMenu")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QToolBar(MainWindow)
        self.toolBar.setObjectName(u"toolBar")
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
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.actionLoad_video.setText(QCoreApplication.translate("MainWindow", u"Load video", None))
        self.actionExit.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.actionSave_Filter.setText(QCoreApplication.translate("MainWindow", u"Save Filter", None))
        self.actionLoad_Filter_2.setText(QCoreApplication.translate("MainWindow", u"Load Filter", None))
        self.actionSave_Filter_2.setText(QCoreApplication.translate("MainWindow", u"Save Filter", None))
        self.actionExit_2.setText(QCoreApplication.translate("MainWindow", u"Exit", None))
        self.groupBox_4.setTitle(QCoreApplication.translate("MainWindow", u"Calibration Pattern Parameters", None))
        self.label_23.setText(QCoreApplication.translate("MainWindow", u"Distance per pixel:", None))
        self.label_diag_len.setText(QCoreApplication.translate("MainWindow", u"Diagonal distance:", None))
        self.label_24.setText(QCoreApplication.translate("MainWindow", u"Length units:", None))
        self.label_pattern_nxm.setText(QCoreApplication.translate("MainWindow", u"Pattern:", None))
        self.label_26.setText(QCoreApplication.translate("MainWindow", u"X", None))
        self.label_pattern_type.setText(QCoreApplication.translate("MainWindow", u"Pattern type: ", None))
        self.comboBox_pattern_type.setItemText(0, QCoreApplication.translate("MainWindow", u"Checkerboard", None))
        self.comboBox_pattern_type.setItemText(1, QCoreApplication.translate("MainWindow", u"Asymmetric Dots", None))

        self.comboBox.setItemText(0, QCoreApplication.translate("MainWindow", u"[mm]", None))
        self.comboBox.setItemText(1, QCoreApplication.translate("MainWindow", u"[in]", None))
        self.comboBox.setItemText(2, QCoreApplication.translate("MainWindow", u"[cm]", None))

        self.pushButton_save_calib.setText(QCoreApplication.translate("MainWindow", u"Save Calibration", None))
        self.groupBox_5.setTitle(QCoreApplication.translate("MainWindow", u"Load images", None))
        self.pushButton.setText(QCoreApplication.translate("MainWindow", u"Load Calibration Images", None))
        self.pushButton_2.setText(QCoreApplication.translate("MainWindow", u"Select Orientation Images", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_8), QCoreApplication.translate("MainWindow", u"Calibrate", None))
        self.pushButton_loadVideo.setText(QCoreApplication.translate("MainWindow", u"Load Video", None))
        self.groupBox_2.setTitle(QCoreApplication.translate("MainWindow", u"Input parameters", None))
        self.label_3.setText(QCoreApplication.translate("MainWindow", u"Flow direction:", None))
        self.label_4.setText(QCoreApplication.translate("MainWindow", u"Filter Method:", None))
        self.label_display_shock.setText(QCoreApplication.translate("MainWindow", u"Display Shock?", None))
        self.comboBox_flowDirection.setItemText(0, QCoreApplication.translate("MainWindow", u"right", None))
        self.comboBox_flowDirection.setItemText(1, QCoreApplication.translate("MainWindow", u"left", None))

        self.checkBox_display_shock.setText("")
        self.label_7.setText(QCoreApplication.translate("MainWindow", u"Frame Index:", None))
        self.comboBox_filterType.setItemText(0, QCoreApplication.translate("MainWindow", u"CNN", None))
        self.comboBox_filterType.setItemText(1, QCoreApplication.translate("MainWindow", u"AutoHSV", None))
        self.comboBox_filterType.setItemText(2, QCoreApplication.translate("MainWindow", u"HSV", None))
        self.comboBox_filterType.setItemText(3, QCoreApplication.translate("MainWindow", u"GRAY", None))

        self.label_19.setText(QCoreApplication.translate("MainWindow", u"X (min:max)", None))
        self.label_21.setText(QCoreApplication.translate("MainWindow", u"Y (min:max)", None))
        self.applyCrop.setText(QCoreApplication.translate("MainWindow", u"Apply", None))
        self.checkBox_crop.setText(QCoreApplication.translate("MainWindow", u"Show crop?", None))
        self.checkBox_annotate.setText(QCoreApplication.translate("MainWindow", u"Annotate?", None))
        self.FilterTabs.setTabText(self.FilterTabs.indexOf(self.tab_7), QCoreApplication.translate("MainWindow", u"Crop", None))
        self.label_8.setText(QCoreApplication.translate("MainWindow", u"Hue (0-180)", None))
        self.label_9.setText(QCoreApplication.translate("MainWindow", u"Saturation (0-255)", None))
        self.label_5.setText(QCoreApplication.translate("MainWindow", u"Value (0-255)", None))
        self.FilterTabs.setTabText(self.FilterTabs.indexOf(self.tab_3), QCoreApplication.translate("MainWindow", u"Model Filter", None))
        self.label_15.setText(QCoreApplication.translate("MainWindow", u"Hue (0-180)", None))
        self.label_16.setText(QCoreApplication.translate("MainWindow", u"Saturation (0-255)", None))
        self.label_6.setText(QCoreApplication.translate("MainWindow", u"Value (0-255)", None))
        self.FilterTabs.setTabText(self.FilterTabs.indexOf(self.tab_4), QCoreApplication.translate("MainWindow", u"Shock Filter", None))
        self.pushButton_save_frame.setText(QCoreApplication.translate("MainWindow", u"Save Current Frame", None))
        self.groupBox.setTitle(QCoreApplication.translate("MainWindow", u"Output parameters", None))
        self.label_17.setText(QCoreApplication.translate("MainWindow", u"Frame range:", None))
        self.label_10.setText(QCoreApplication.translate("MainWindow", u"Process every Nth:", None))
        self.label_20.setText(QCoreApplication.translate("MainWindow", u"Output filename:", None))
        self.checkBox_writeVideo.setText(QCoreApplication.translate("MainWindow", u"Write video?", None))
        self.pushButton_process.setText(QCoreApplication.translate("MainWindow", u"Process All", None))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QCoreApplication.translate("MainWindow", u"Extract Edges", None))
        self.pushButton_LoadFiles.setText(QCoreApplication.translate("MainWindow", u"Load Files", None))
        self.pushButton_export_csv.setText(QCoreApplication.translate("MainWindow", u"Export CSV", None))
        self.pushButton_PlotData.setText(QCoreApplication.translate("MainWindow", u"Plot Data", None))
        self.pushButton_fitData.setText(QCoreApplication.translate("MainWindow", u"Fit Data", None))
        self.label.setText(QCoreApplication.translate("MainWindow", u"Model diameter: ", None))
        self.label_11.setText(QCoreApplication.translate("MainWindow", u"Length units:", None))
        self.comboBox_units.setItemText(0, QCoreApplication.translate("MainWindow", u"[in]", None))
        self.comboBox_units.setItemText(1, QCoreApplication.translate("MainWindow", u"[cm]", None))
        self.comboBox_units.setItemText(2, QCoreApplication.translate("MainWindow", u"[mm]", None))
        self.comboBox_units.setItemText(3, QCoreApplication.translate("MainWindow", u"pixels", None))

        self.label_18.setText(QCoreApplication.translate("MainWindow", u"Frames per sec:", None))
        self.label_2.setText(QCoreApplication.translate("MainWindow", u"Mask nframes:", None))
        self.label_display_shock2.setText(QCoreApplication.translate("MainWindow", u"Display Shock", None))
        self.checkBox_display_shock2.setText("")
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_5), QCoreApplication.translate("MainWindow", u"Plotting params", None))
        self.groupBox_3.setTitle(QCoreApplication.translate("MainWindow", u"Fitting Parameters", None))
        self.label_12.setText(QCoreApplication.translate("MainWindow", u"Fit type:", None))
        self.comboBox_fit_type.setItemText(0, QCoreApplication.translate("MainWindow", u"linear", None))

        self.label_13.setText(QCoreApplication.translate("MainWindow", u"Start time:", None))
        self.label_14.setText(QCoreApplication.translate("MainWindow", u"End time:", None))
        self.tabWidget_2.setTabText(self.tabWidget_2.indexOf(self.tab_6), QCoreApplication.translate("MainWindow", u"Fitting params", None))
        self.groupBox_XT_params.setTitle(QCoreApplication.translate("MainWindow", u"Visible Traces on XT plot", None))
        self.checkBox_shock_center.setText(QCoreApplication.translate("MainWindow", u"Shock center", None))
        self.checkBox_m95_radius.setText(QCoreApplication.translate("MainWindow", u"-95% radius", None))
        self.checkBox_shockmodel.setText(QCoreApplication.translate("MainWindow", u"Shock-model dist", None))
        self.checkBox_ypos.setText(QCoreApplication.translate("MainWindow", u"Model axis-position", None))
        self.checkBox_m50_radius.setText(QCoreApplication.translate("MainWindow", u"-50% radius", None))
        self.checkBox_shock_area.setText(QCoreApplication.translate("MainWindow", u"Shock area", None))
        self.checkBox_95_radius.setText(QCoreApplication.translate("MainWindow", u"+95% radius", None))
        self.checkBox_model_center.setText(QCoreApplication.translate("MainWindow", u"Model center", None))
        self.checkBox_50_radius.setText(QCoreApplication.translate("MainWindow", u"+50% radius ", None))
        self.checkBox_model_rad.setText(QCoreApplication.translate("MainWindow", u"Model radius", None))
        self.groupBox_data_summary.setTitle(QCoreApplication.translate("MainWindow", u"Data Summary", None))
        self.label_data_summary.setText("")
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QCoreApplication.translate("MainWindow", u"Analyze", None))
        self.basebar.setText("")
        self.menuMenu.setTitle(QCoreApplication.translate("MainWindow", u"Menu", None))
        self.toolBar.setWindowTitle(QCoreApplication.translate("MainWindow", u"toolBar", None))
    # retranslateUi

