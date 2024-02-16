import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QTabWidget


# Import your existing GUI classes
from segment_gui import MainWindow as Gui1MainWindow
from samqt import MainWindow as Gui2MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Create the main application window
    main_window = QMainWindow()

    # Create a QTabWidget to hold the two tabs
    tab_widget = QTabWidget(main_window)

    # Create instances of your existing GUIs and add them to the tabs
    gui1 = Gui1MainWindow()
    gui2 = Gui2MainWindow()

    tab_widget.addTab(gui1, "Grabcut segmentation")
    tab_widget.addTab(gui2, "SAM segmentation")

    # Set the QTabWidget as the central widget for the main window
    main_window.setCentralWidget(tab_widget)

    main_window.show()
    sys.exit(app.exec_())