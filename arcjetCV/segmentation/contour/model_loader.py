import urllib.request
from pathlib import Path
import os
import hashlib
from PySide6.QtWidgets import (
    QApplication,
    QMessageBox,
    QDialog,
    QVBoxLayout,
    QLabel,
    QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal


# -------------------- CONFIG --------------------

MODEL_NAME = "Unet-xception_25_weights_only.pt"
MODEL_URL = "https://github.com/magnus-haw/arcjetCV/raw/main/arcjetCV/segmentation/contour/Unet-xception_25_weights_only.pt"
EXPECTED_HASH = "adcfd0e04c51be32b69e8ab1139c172df8c3e9c2fc85844db2c8926240631171"


# -------------------- SHA256 CHECK --------------------


def verify_sha256(path: Path, expected_hash: str) -> bool:
    if not path.exists():
        return False
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest() == expected_hash


# -------------------- BACKGROUND DOWNLOAD THREAD --------------------


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


# -------------------- POPUP WIDGET --------------------


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


# -------------------- MAIN FUNCTION --------------------


def get_model_checkpoint():
    checkpoint_path = Path(__file__).parent / MODEL_NAME

    # If file doesn't exist or hash is incorrect, download
    if not verify_sha256(checkpoint_path, EXPECTED_HASH):
        app = QApplication.instance() or QApplication([])
        popup = DownloadPopup(MODEL_URL, str(checkpoint_path))
        if not popup.exec():
            raise RuntimeError("Download canceled or failed.")

        if not verify_sha256(checkpoint_path, EXPECTED_HASH):
            raise RuntimeError("Download failed or file corrupted (hash mismatch).")

    return checkpoint_path
