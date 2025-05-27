import torch
from pathlib import Path
import cv2
from torchvision import transforms as T
import segmentation_models_pytorch as smp
import urllib.request


class CNN:
    def __init__(self):
        # Automatically choose GPU if available
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        model_name = "Unet-xception_25_weights_only.pt"
        self.checkpoint_path = Path(__file__).parent / model_name
        self.expected_hash = (
            "adcfd0e04c51be32b69e8ab1139c172df8c3e9c2fc85844db2c8926240631171"
        )
        self.download_url = "https://github.com/magnus-haw/arcjetCV/raw/main/arcjetCV/segmentation/contour/Unet-xception_25_weights_only.pt"

        if not self._verify_model():
            self._download_model()

        self.checkpoint_path = (
            Path(__file__)
            .parent.absolute()
            .joinpath("Unet-xception_25_weights_only.pt")
        )

        self.model = smp.Unet(
            encoder_name="xception",
            encoder_weights=None,
            classes=4,  # match saved model
            activation=None,
        )
        self.model.load_state_dict(
            torch.load(
                self.checkpoint_path, map_location=self.device, weights_only=False
            )
        )
        self.model.to(self.device)
        self.model.eval()

        self.mean = [0.485, 0.456, 0.406]
        self.std = [0.229, 0.224, 0.225]
        self.t = T.Compose(
            [
                T.ToPILImage(),
                T.Resize((512, 512)),
                T.ToTensor(),
                T.Normalize(self.mean, self.std),
            ]
        )

    def predict(self, img):

        self.model.eval()
        image = self.t(img)

        self.model.to(self.device)
        image = image.to(self.device)

        with torch.no_grad():
            image = image.unsqueeze(0)
            output = self.model(image)
            masked = torch.argmax(output, dim=1)
            masked = masked.cpu().squeeze(0).numpy()

        masked = cv2.resize(
            masked, (img.shape[1], img.shape[0]), interpolation=cv2.INTER_NEAREST
        )
        return masked

    def _verify_model(self):
        """Return True if model file exists and matches expected SHA256 hash."""
        if not self.checkpoint_path.exists():
            return False
        h = hashlib.sha256()
        with self.checkpoint_path.open("rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest() == self.expected_hash

    def _download_model(self):
        """Download model weights from URL and verify the hash."""
        print(f"[INFO] Downloading model weights to {self.checkpoint_path}...")
        urllib.request.urlretrieve(self.download_url, self.checkpoint_path)
        if not self._verify_model():
            raise ValueError("[ERROR] Model download failed: hash mismatch.")
        print("[INFO] Model downloaded and verified successfully.")
