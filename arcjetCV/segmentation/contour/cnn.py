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

        # Download if missing
        if not self.checkpoint_path.exists():
            print(f"[INFO] Downloading model weights to {self.checkpoint_path}...")
            url = "https://github.com/magnus-haw/arcjetCV/blob/main/arcjetCV/segmentation/contour/Unet-xception_25_weights_only.pt"
            urllib.request.urlretrieve(url, self.checkpoint_path)

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
            torch.load(self.checkpoint_path, map_location=self.device)
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
