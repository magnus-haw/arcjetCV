import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import interpolate
from pathlib import Path


def _torch_load_compat(path, **kwargs):
    try:
        return torch.load(path, weights_only=False, **kwargs)
    except TypeError:
        return torch.load(path, **kwargs)


def extract_interest(signal):
    """Extract the starts and ends of a signal that is the mean brightness of frames
    Args:
        signal (array): mean brightness signal of frames
    Returns:
        arrays: start and end indexes
    """
    start = []
    end = []
    for index, i in enumerate(signal):
        if index == 0 and i > 0.5:
            start.append(index)
        elif signal[index - 1] <= 0.5 and i > 0.5:
            start.append(index)
        elif signal[index - 1] >= 0.5 and i < 0.5:
            end.append(index)
    if signal[-1] > 0.5:
        end.append(len(signal) - 1)
    return start, end


def time_segmentation(video, progress_callback=None):
    """apply a segmentation on a the mean brightness of frames of a video
    """
    max_sampled_frames = 120
    baseline_samples = max(2, ((video.nframes - 1) // 10) + 1)
    nsamples = min(max_sampled_frames, baseline_samples)
    sample_indices = np.linspace(0, video.nframes - 1, num=nsamples, dtype=int)

    nFrame = []
    Value = []
    if progress_callback is not None:
        progress_callback(0, "Detecting sample insertion")
    for frame_index in sample_indices:
        try:
            _frame = video.get_frame(int(frame_index))
            h = _frame.shape[0]
            y0 = int(0.2 * h)
            y1 = int(0.8 * h)
            roi = _frame[y0:y1, :]
            if roi.size == 0:
                continue

            # Downsample before computing brightness to speed up loading on large frames.
            max_dim = 256
            if max(roi.shape[0], roi.shape[1]) > max_dim:
                scale = max_dim / float(max(roi.shape[0], roi.shape[1]))
                roi = cv2.resize(
                    roi,
                    (
                        max(1, int(roi.shape[1] * scale)),
                        max(1, int(roi.shape[0] * scale)),
                    ),
                    interpolation=cv2.INTER_AREA,
                )

            # Keep feature extraction aligned with the checkpoint training pipeline:
            # erode + HSV V-channel brightness.
            kernel = np.ones((20, 20), np.uint8)
            roi = cv2.erode(roi, kernel, cv2.BORDER_REFLECT)
            hsv = cv2.cvtColor(roi, cv2.COLOR_RGB2HSV)
            Value.append(np.mean(hsv[:, :, 2]))
            nFrame.append((frame_index / max(1, video.nframes - 1)) * 500.0)
            if progress_callback is not None:
                progress = int((len(Value) / max(1, nsamples)) * 100)
                progress_callback(progress, "Detecting sample insertion...")
        except Exception:
            pass

    if len(Value) < 2:
        raise RuntimeError("Insufficient sampled frames for time segmentation.")

    Value = np.array(Value, dtype=float)
    value_range = np.ptp(Value)
    if value_range <= 0:
        raise RuntimeError("Brightness signal is constant; cannot segment in time.")
    Value = (Value - np.min(Value)) / value_range

    nFrame = np.array(nFrame, dtype=float)
    p = interpolate.interp1d(nFrame, Value, fill_value="extrapolate")
    reg = np.linspace(0, 500, 500)

    model = Conv1DNet()
    checkpoint_path = Path(__file__).parent.absolute().joinpath(Path('time-checkpoint.pt'))
    model.load_state_dict(_torch_load_compat(checkpoint_path))
    if progress_callback is not None:
        progress_callback(100, "Detecting sample insertion")
    input = np.array(p(reg))

    # Prepare input tensor with shape [1, 1, 500]
    input = torch.tensor(input, dtype=torch.float).unsqueeze(0).unsqueeze(1)
    model.eval()  # Switch to evaluation mode
    with torch.no_grad():  # Disable gradient computation
        test_output = model(input)
        probabilities = F.softmax(
            test_output, dim=1
        )  # Optional: convert logits to probabilities
        predictions = torch.argmax(probabilities, dim=1).squeeze()  # Predicted classes

    # Flatten input and probabilities for plotting and analysis
    input = input.squeeze().cpu().numpy()
    out = predictions.squeeze().cpu().numpy()

    return input, out


class Conv1DNet(nn.Module):
    def __init__(self):
        super(Conv1DNet, self).__init__()
        self.conv1 = nn.Conv1d(
            in_channels=1, out_channels=32, kernel_size=7, stride=2, padding=3
        )
        self.conv2 = nn.Conv1d(
            in_channels=32, out_channels=16, kernel_size=7, stride=2, padding=3
        )
        self.convtrans1 = nn.ConvTranspose1d(
            in_channels=16,
            out_channels=16,
            kernel_size=7,
            stride=2,
            padding=3,
            output_padding=1,
        )
        self.convtrans2 = nn.ConvTranspose1d(
            in_channels=16,
            out_channels=32,
            kernel_size=7,
            stride=2,
            padding=3,
            output_padding=1,
        )
        self.convtrans3 = nn.ConvTranspose1d(
            in_channels=32, out_channels=3, kernel_size=3, stride=1, padding=1
        )
        self.dropout = nn.Dropout(0.25)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = self.dropout(x)
        x = F.relu(self.conv2(x))
        x = self.dropout(x)
        x = F.relu(self.convtrans1(x))
        x = self.dropout(x)
        x = F.relu(self.convtrans2(x))
        x = self.dropout(x)
        x = self.convtrans3(x)
        # Applying softmax on the last dimension (channels) to get probabilities
        x = F.softmax(x, dim=1)
        return x
