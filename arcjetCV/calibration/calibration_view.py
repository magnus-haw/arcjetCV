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
import matplotlib.image as mpimg
import os
from pathlib import Path


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
        self.load_button = QPushButton("Load Calibration Images")
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

        # # 1. Pattern Type Selection
        # pattern_type_layout = QHBoxLayout()
        # pattern_type_label_n = QLabel("1.")
        # pattern_type_label = QLabel("Pattern Type:")
        # self.pattern_type_combo = QComboBox()
        # self.pattern_type_combo.addItems(["Chessboard", "Circles"])  # Dropdown options

        # # Add widgets to the layout
        # pattern_type_layout.addWidget(pattern_type_label_n)
        # pattern_type_layout.addWidget(pattern_type_label)
        # pattern_type_layout.addWidget(
        #     self.pattern_type_combo, stretch=1
        # )  # Allow ComboBox to expand
        # pattern_resolution_layout.addLayout(pattern_type_layout)

        # 1. Grid Size Input
        grid_size_layout = QHBoxLayout()
        grid_size_label_n = QLabel("1.")
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

        # 2. Load Image for Resolution Measurement
        load_image_layout_pattern = QHBoxLayout()
        load_image_layout_pattern.setContentsMargins(0, 0, 0, 0)
        load_image_label_pattern = QLabel("2.")
        self.load_image_button_pattern = QPushButton(
            "Load Image for Resolution Measurement"
        )
        self.load_image_button_pattern.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        load_image_layout_pattern.addWidget(load_image_label_pattern)
        load_image_layout_pattern.addWidget(self.load_image_button_pattern, stretch=1)
        pattern_resolution_layout.addLayout(load_image_layout_pattern)

        # 4. Diagonal Distance Line
        diagonal_distance_layout = QHBoxLayout()
        diagonal_distance_layout.setContentsMargins(
            0, 0, 0, 0
        )  # Remove default margins
        diagonal_distance_label_n = QLabel("3.")
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

        # 4. Get Resolution Button
        get_resolution_layout = QHBoxLayout()
        get_resolution_label = QLabel("4.")
        self.get_resolution_button = QPushButton("Calculate Resolution")
        get_resolution_layout.addWidget(get_resolution_label)
        get_resolution_layout.addWidget(self.get_resolution_button, stretch=1)
        pattern_resolution_layout.addLayout(get_resolution_layout)

        # Ruler Resolution Tab
        self.ruler_resolution_tab = QWidget()
        ruler_resolution_layout = QVBoxLayout()
        self.ruler_resolution_tab.setLayout(ruler_resolution_layout)
        self.resolution_tabs.addTab(self.ruler_resolution_tab, "Ruler Resolution")

        # 1. Load Image for Resolution Measurement
        load_image_layout = QHBoxLayout()
        load_image_layout.setContentsMargins(0, 0, 0, 0)  # Remove default margins
        load_image_label = QLabel("1.")
        self.load_image_button = QPushButton("Load Image for Resolution Measurement")
        self.load_image_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )  # Expand button
        load_image_layout.addWidget(load_image_label)
        load_image_layout.addWidget(self.load_image_button, stretch=1)
        ruler_resolution_layout.addLayout(load_image_layout)

        # 2. Draw a Line
        draw_line_layout = QHBoxLayout()
        draw_line_layout.setContentsMargins(0, 0, 0, 0)  # No extra margins for the row
        draw_line_label = QLabel("2.")
        self.instruction_label = QLabel("Draw a line of a known distance on the image")
        self.instruction_label.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        draw_line_layout.addWidget(draw_line_label)
        draw_line_layout.addWidget(self.instruction_label, stretch=1)
        ruler_resolution_layout.addLayout(draw_line_layout)

        # 3. Enter Real-World Length
        real_world_length_layout = QHBoxLayout()
        real_world_length_layout.setContentsMargins(
            0, 0, 0, 0
        )  # No extra margins for the row
        real_world_length_label_n = QLabel("3.")
        real_world_length_label = QLabel("Real-World Length:")
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Enter real-world length in mm")
        self.distance_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        real_world_length_layout.addWidget(real_world_length_label_n)
        real_world_length_layout.addWidget(real_world_length_label)
        real_world_length_layout.addWidget(self.distance_input, stretch=1)
        ruler_resolution_layout.addLayout(real_world_length_layout)

        # 4. Calculate Resolution Button
        calculate_resolution_layout = QHBoxLayout()
        calculate_resolution_layout.setContentsMargins(
            0, 0, 0, 0
        )  # No extra margins for the row
        calculate_resolution_label_n = QLabel("4.")
        self.calculate_button = QPushButton("Calculate Resolution")
        self.calculate_button.setSizePolicy(
            QSizePolicy.Expanding, QSizePolicy.Preferred
        )
        calculate_resolution_layout.addWidget(calculate_resolution_label_n)
        calculate_resolution_layout.addWidget(self.calculate_button)
        ruler_resolution_layout.addLayout(calculate_resolution_layout)

        # Display PPCM Result
        # Inside image_resolution_layout
        self.ppcm_label = QLabel("Pixels per mm: N/A")
        self.image_resolution_layout.addWidget(self.ppcm_label)
        self.ruler_resolution_tab.setLayout(ruler_resolution_layout)

        # Add tabs to the resolution group
        self.image_resolution_group.setLayout(self.image_resolution_layout)
        button_layout.addWidget(self.image_resolution_group)

        # Save Calibration Button
        self.save_calibration_button = QPushButton("Save Calibration")
        button_layout.addWidget(self.save_calibration_button)

        # Add button layout to main layout
        main_layout.addLayout(button_layout, stretch=1)
        self.setLayout(main_layout)
        button_layout.addStretch()

        self.plot_logo()

    def plot_logo(self):
        """Plots the ArcjetCV logo on the Matplotlib canvas."""
        try:
            self.figure.clear()  # Clear the canvas
            ax = self.figure.add_subplot(111)

            # Load the logo
            logo_path = os.path.join(
                Path(__file__).parent.absolute(), "../gui/logo/arcjetCV_logo_white.png"
            )
            logo_image = mpimg.imread(logo_path)

            # Display the logo
            ax.imshow(logo_image)
            ax.axis("off")  # Turn off axes for a cleaner look

            self.canvas.draw()  # Refresh the canvas
        except Exception as e:
            print(f"Error plotting logo: {e}")
