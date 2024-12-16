from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QGroupBox,
    QTabWidget,
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class CalibrationView(QWidget):
    def __init__(self):
        super().__init__()

        # Main layout: horizontal
        main_layout = QHBoxLayout()

        # Left side: Matplotlib canvas
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        canvas_layout = QVBoxLayout()
        canvas_layout.addWidget(self.canvas)
        main_layout.addLayout(canvas_layout, stretch=3)

        # Right side: buttons and inputs
        button_layout = QVBoxLayout()

        # Pattern Calibration Section
        self.pattern_calibration_group = QGroupBox("1. Intrinsic Calibration")
        self.pattern_calibration_layout = QVBoxLayout()

        # Adding Pattern Calibration Buttons
        self.print_button = QPushButton("Print Chessboard")
        self.load_button = QPushButton("Load Chessboard Images")
        self.calibrate_button = QPushButton("Calibrate Camera")
        self.image_label = QLabel("No images loaded")

        self.pattern_calibration_layout.addWidget(self.print_button)
        self.pattern_calibration_layout.addWidget(self.load_button)
        self.pattern_calibration_layout.addWidget(self.calibrate_button)
        self.pattern_calibration_layout.addWidget(self.image_label)
        self.pattern_calibration_group.setLayout(self.pattern_calibration_layout)

        button_layout.addWidget(self.pattern_calibration_group)
        button_layout.addSpacing(20)

        # Image Resolution Section
        self.image_resolution_group = QGroupBox("2. Metric Calibration")
        self.image_resolution_layout = QVBoxLayout()

        self.resolution_tabs = QTabWidget()
        self.image_resolution_layout.addWidget(self.resolution_tabs)

        # Pattern Resolution Tab
        self.pattern_resolution_tab = QWidget()
        pattern_resolution_layout = QVBoxLayout()
        self.pattern_resolution_tab.setLayout(pattern_resolution_layout)
        self.resolution_tabs.addTab(self.pattern_resolution_tab, "Pattern Resolution")

        # Diagonal Distance Line
        diagonal_distance_layout = QHBoxLayout()
        diagonal_distance_label = QLabel("Diagonal Distance:")
        self.diagonal_distance_value = QLineEdit("0.00")
        diagonal_distance_layout.addWidget(diagonal_distance_label)
        diagonal_distance_layout.addWidget(self.diagonal_distance_value)
        pattern_resolution_layout.addLayout(diagonal_distance_layout)
        # Ruler Resolution Tab
        self.ruler_resolution_tab = QWidget()
        ruler_resolution_layout = QVBoxLayout()

        # 1. Load Image for Resolution Measurement
        load_image_layout = QHBoxLayout()
        load_image_label = QLabel("1.")
        self.load_image_button = QPushButton("Load Image for Resolution Measurement")
        load_image_layout.addWidget(load_image_label)
        load_image_layout.addWidget(self.load_image_button)
        ruler_resolution_layout.addLayout(load_image_layout)

        # 2. Draw a Line
        draw_line_layout = QHBoxLayout()
        draw_line_label = QLabel("2.")
        self.instruction_label = QLabel("Draw a line of a known distance on the image")
        draw_line_layout.addWidget(draw_line_label)
        draw_line_layout.addWidget(self.instruction_label)
        ruler_resolution_layout.addLayout(draw_line_layout)

        # 3. Enter Real-World Length and Calculate
        real_world_layout = QHBoxLayout()
        real_world_label = QLabel("3.")
        self.cm_input = QLineEdit()
        self.cm_input.setPlaceholderText("Enter real-world length in cm")
        self.calculate_button = QPushButton("Get Resolutions")
        real_world_layout.addWidget(real_world_label)
        real_world_layout.addWidget(self.cm_input)
        real_world_layout.addWidget(self.calculate_button)
        ruler_resolution_layout.addLayout(real_world_layout)

        # Display PPCM Result
        # Inside image_resolution_layout
        self.ppcm_label = QLabel("Pixels per mm: N/A")
        self.image_resolution_layout.addWidget(self.ppcm_label)
        self.ruler_resolution_tab.setLayout(ruler_resolution_layout)

        # Add tabs to the resolution group
        self.resolution_tabs.addTab(self.ruler_resolution_tab, "Ruler Resolution")
        self.image_resolution_group.setLayout(self.image_resolution_layout)
        button_layout.addWidget(self.image_resolution_group)
        button_layout.addStretch()

        # Add button layout to main layout
        main_layout.addLayout(button_layout, stretch=1)

        self.setLayout(main_layout)
