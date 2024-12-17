from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QLineEdit,
    QGroupBox,
    QTabWidget,
    QComboBox,
    QSizePolicy,
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

        # 1. Pattern Type Selection
        pattern_type_layout = QHBoxLayout()
        pattern_type_label_n = QLabel("1.")
        pattern_type_label = QLabel("Pattern Type:")
        self.pattern_type_combo = QComboBox()
        self.pattern_type_combo.addItems(["Chessboard", "Circles"])  # Dropdown options

        # Add widgets to the layout
        pattern_type_layout.addWidget(pattern_type_label_n)
        pattern_type_layout.addWidget(pattern_type_label)
        pattern_type_layout.addWidget(
            self.pattern_type_combo, stretch=1
        )  # Allow ComboBox to expand
        pattern_resolution_layout.addLayout(pattern_type_layout)

        # 2. Grid Size Input
        grid_size_layout = QHBoxLayout()
        grid_size_label_n = QLabel("2.")
        grid_size_label = QLabel("Grid Size:")
        self.grid_rows_input = QLineEdit("9")  # Default rows
        self.grid_cols_input = QLineEdit("6")  # Default columns
        grid_size_layout.addWidget(grid_size_label_n)
        grid_size_layout.addWidget(grid_size_label)
        grid_size_layout.addWidget(QLabel("Rows:"))
        grid_size_layout.addWidget(self.grid_rows_input)
        grid_size_layout.addWidget(QLabel("Cols:"))
        grid_size_layout.addWidget(self.grid_cols_input)
        pattern_resolution_layout.addLayout(grid_size_layout)

        # 3. Load Image for Resolution Measurement
        load_image_layout_pattern = QHBoxLayout()
        load_image_layout_pattern.setContentsMargins(
            0, 0, 0, 0
        )  # Remove default margins
        load_image_label_pattern = QLabel("3.")
        self.load_image_button_pattern = QPushButton(
            "Load Image for Resolution Measurement"
        )
        self.load_image_button_pattern.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )  # Expand button
        load_image_layout_pattern.addWidget(load_image_label_pattern)
        load_image_layout_pattern.addWidget(self.load_image_button_pattern, stretch=1)
        pattern_resolution_layout.addLayout(load_image_layout_pattern)

        # 4. Diagonal Distance Line
        diagonal_distance_layout = QHBoxLayout()
        diagonal_distance_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove default margins
        diagonal_distance_label_n = QLabel("4.")
        diagonal_distance_label = QLabel("Diagonal Distance:")
        self.diagonal_distance_value = QLineEdit("0.00")
        self.diagonal_distance_value.setPlaceholderText("Real-world length in mm")
        self.diagonal_distance_value.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )  # Expand QLineEdit
        diagonal_distance_layout.addWidget(diagonal_distance_label_n)
        diagonal_distance_layout.addWidget(diagonal_distance_label)
        diagonal_distance_layout.addWidget(self.diagonal_distance_value, stretch=1)
        pattern_resolution_layout.addLayout(diagonal_distance_layout)

        # 5. Get Resolution Button
        get_resolution_layout = QHBoxLayout()
        get_resolution_label = QLabel("5.")
        self.get_resolution_button = QPushButton("Get Resolution")

        # Add widgets to the layout
        get_resolution_layout.addWidget(get_resolution_label)
        get_resolution_layout.addWidget(
            self.get_resolution_button, stretch=1
        )  # Allow button to expand
        pattern_resolution_layout.addLayout(get_resolution_layout)

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
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Enter real-world length in mm")
        self.calculate_button = QPushButton("Get Resolutions")
        real_world_layout.addWidget(real_world_label)
        real_world_layout.addWidget(self.distance_input)
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
