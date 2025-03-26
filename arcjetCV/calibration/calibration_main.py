from PySide6.QtWidgets import QApplication
from calibration_controller import CalibrationController
from calibration_view import CalibrationView
import sys


def main():
    app = QApplication(sys.argv)
    view = CalibrationView()
    controller = CalibrationController(view)
    view.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
