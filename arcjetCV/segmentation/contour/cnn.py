import torch
from pathlib import Path
import cv2
from torchvision import transforms as T
import os
import segmentation_models_pytorch as smp


def _torch_load_compat(path, **kwargs):
    try:
        return torch.load(path, weights_only=False, **kwargs)
    except TypeError:
        return torch.load(path, **kwargs)


def _is_lfs_pointer(path):
    try:
        with open(path, "rb") as fin:
            head = fin.read(64)
        return head.startswith(b"version https://git-lfs.github.com/spec/v1")
    except OSError:
        return False


def _resolve_checkpoint_path():
    env_path = os.environ.get("ARCJETCV_CNN_WEIGHTS")
    if env_path:
        candidate = Path(env_path).expanduser()
        if candidate.exists():
            return candidate
        raise FileNotFoundError(
            f"ARCJETCV_CNN_WEIGHTS path does not exist: {candidate}"
        )

    base_dir = Path(__file__).parent.absolute()
    candidates = [
        base_dir.joinpath(Path("Unet-xception_25_weights_only.pt")),
        base_dir.joinpath(Path("Unet-xception_25_original.pt")),
        base_dir.joinpath(Path("Unet-xception-last-checkpoint.pt")),
    ]
    for candidate in candidates:
        if candidate.exists() and not _is_lfs_pointer(candidate):
            return candidate

    raise FileNotFoundError(
        "CNN checkpoint not found. "
        "The .pt file appears to be a Git LFS pointer or is missing. "
        "Download real weights (git-lfs pull) or set ARCJETCV_CNN_WEIGHTS."
    )


class CNN:
    def __init__(self):
        # predict fails from GUI (Could not load library libcudnn_ops_infer.so), works from script. Fix: run it cpu only
        self.device = torch.device(
            "cpu"
        )  # torch.device("cuda") if torch.cuda.is_available() else torch.device("cpu")

        self.checkpoint_path = _resolve_checkpoint_path()
        try:
            loaded = _torch_load_compat(self.checkpoint_path, map_location=self.device)
        except Exception:
            # If preferred checkpoint is incompatible, try known local alternatives.
            base_dir = Path(__file__).parent.absolute()
            fallbacks = [
                base_dir.joinpath(Path("Unet-xception_25_weights_only.pt")),
                base_dir.joinpath(Path("Unet-xception_25_original.pt")),
                base_dir.joinpath(Path("Unet-xception-last-checkpoint.pt")),
            ]
            loaded = None
            for candidate in fallbacks:
                if candidate == self.checkpoint_path:
                    continue
                if not candidate.exists() or _is_lfs_pointer(candidate):
                    continue
                try:
                    loaded = _torch_load_compat(candidate, map_location=self.device)
                    self.checkpoint_path = candidate
                    break
                except Exception:
                    continue
            if loaded is None:
                raise
        if isinstance(loaded, dict):
            # Weights-only checkpoint: rebuild training architecture then load params.
            model = smp.Unet("xception", classes=4, encoder_weights=None)
            model.load_state_dict(loaded)
            self.model = model
        else:
            # Full serialized model checkpoint.
            self.model = loaded

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
