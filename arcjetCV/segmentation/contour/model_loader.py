import urllib.request
from pathlib import Path
import os


def get_model_checkpoint():
    model_name = "Unet-xception_25_weights_only.pt"
    checkpoint_path = Path(__file__).parent / model_name

    if not checkpoint_path.exists():
        print(f"[INFO] Downloading model weights to {checkpoint_path}...")
        url = "https://github.com/magnus-haw/arcjetCV/raw/main/arcjetCV/segmentation/contour/Unet-xception_25_weights_only.pt"
        try:
            urllib.request.urlretrieve(url, checkpoint_path)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to download model weights: {e}")

    return checkpoint_path
