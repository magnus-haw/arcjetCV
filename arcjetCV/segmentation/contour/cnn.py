import torch
from pathlib import Path
import cv2
from torchvision import transforms as T


class CNN:
    def __init__(self):
        # predict fails from GUI (Could not load library libcudnn_ops_infer.so), works from script. Fix: run it cpu only
        self.device = torch.device(
            "cpu"
        )  # torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        self.checkpoint_path = (
            Path(__file__)
            .parent.absolute()
            .joinpath(Path("Unet-xception_25_original.pt"))
        )
        self.model = torch.load(self.checkpoint_path, map_location=self.device)

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
