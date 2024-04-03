from PySide6 import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure


class TrackLabel(QtWidgets.QLabel):
    newCursorValue = QtCore.Signal(list)

    def mouseMoveEvent(self,event):
        self.newCursorValue.emit([event.x(), event.y(),self.width(), self.height()])


class MplCanvas(FigureCanvas):
    """ Convenience class to embed matplotlib canvas

    Args:
        FigureCanvas (matplotlib object): matplotlib canvas object
    """
    clicked = QtCore.Signal(float, float)

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.figure.set_layout_engine('tight')
        self.axes = self.figure.add_subplot(111)
        super(MplCanvas, self).__init__(self.figure)

        # Connect the mouse click event to the callback function
        self.mpl_connect("button_press_event", self.on_mouse_click)

    def on_mouse_click(self, event):
        if event.button == 1:  # Left mouse button
            x, y = event.xdata, event.ydata
            if x is not None and y is not None:
                self.clicked.emit(x, y)


class MatplotlibWidget(QtWidgets.QWidget):
    """Plotting widget using matplotlib, embedding into Qt

    Args:
        MplCanvas (FigureCanvas): matplotlib standard canvas
    """
    
    def __init__(self,*args):
        super().__init__(*args)
        layout = QtWidgets.QVBoxLayout(self)
        self.canvas = MplCanvas(self)
        toolbar = NavigationToolbar(self.canvas, self)
        layout.addWidget(toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)


class OverlayLabel(QtWidgets.QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | QtCore.Qt.Tool)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

    def showEvent(self, event):
        super().showEvent(event)
        self.resize(self.parent().size())
