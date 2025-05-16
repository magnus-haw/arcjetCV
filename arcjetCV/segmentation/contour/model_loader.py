import urllib.request
from pathlib import Path
import os
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal


class DownloadThread(QThread):
    progress = Signal(int)
    error = Signal(str)
    finished = Signal()

    def __init__(self, url, output_path):
        super().__init__()
        self.url = url
        self.output_path = output_path

    def run(self):
        try:

            def reporthook(blocknum, blocksize, totalsize):
                readsofar = blocknum * blocksize
                percent = int(readsofar * 100 / totalsize) if totalsize > 0 else 0
                self.progress.emit(min(percent, 100))

            urllib.request.urlretrieve(self.url, self.output_path, reporthook)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class DownloadPopup(QDialog):
    def __init__(self, url, output_path):
        super().__init__()
        self.setWindowTitle("Downloading Model Weights")
        self.setWindowFlags(self.windowFlags() | Qt.CustomizeWindowHint)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

        self.layout = QVBoxLayout()
        self.label = QLabel("Downloading model weights, please wait...")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.progress_bar)
        self.setLayout(self.layout)

        self.thread = DownloadThread(url, output_path)
        self.thread.progress.connect(self.progress_bar.setValue)
        self.thread.error.connect(self.show_error)
        self.thread.finished.connect(self.accept)
        self.thread.start()

    def show_error(self, message):
        QMessageBox.critical(self, "Download Failed", f"❌ {message}")
        self.reject()


def get_model_checkpoint():
    model_name = "Unet-xception_25_weights_only.pt"
    checkpoint_path = Path(__file__).parent / model_name
    if not checkpoint_path.exists():
        url = "https://github.com/magnus-haw/arcjetCV/raw/main/arcjetCV/segmentation/contour/Unet-xception_25_weights_only.pt"

        app = QApplication.instance() or QApplication([])
        popup = DownloadPopup(url, str(checkpoint_path))
        if not popup.exec():
            raise RuntimeError("Download canceled or failed.")

    return checkpoint_path
