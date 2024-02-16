from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PySide6.QtWidgets import QSizePolicy


class MplCanvas(FigureCanvas):
    """
    MplCanvas is a class that wraps a Matplotlib figure and creates a canvas that can be embedded into the PySide6 GUI.
    It inherits from FigureCanvasQTAgg, which is a Qt widget that wraps a Matplotlib figure for display.
    """

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        """
        Initializes the canvas with a Matplotlib figure.

        Parameters:
        - parent: The parent widget. Default is None.
        - width: The width of the canvas. Default is 5.
        - height: The height of the canvas. Default is 4.
        - dpi: The dots per inch (resolution) of the canvas. Default is 100.
        """
        # Create a new Matplotlib figure with the given dimensions and resolution.
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.figure.set_tight_layout(True)

        # Add a subplot to the figure. '111' means 1 row, 1 column, first subplot.
        self.ax = self.figure.add_subplot(111)

        # Initialize the parent class with the figure.
        super(MplCanvas, self).__init__(self.figure)

        # Set the parent widget, if provided.
        self.setParent(parent)

        # Adjust the canvas's size policy to be expandable and updatable.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.updateGeometry()
