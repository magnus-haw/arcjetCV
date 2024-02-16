import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import interpolate
from pathlib import Path


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


def time_segmentation(video):
    """apply a segmentation on a the mean brightness of frames of a video
    """
    n = 0
    nFrame = []
    Value = []
    for frame_index in range(0, video.nframes - 1, 10):
        n = n + 1
        try:
            _frame = video.get_frame(frame_index)
            y = _frame.shape[0]
            x = _frame.shape[1]
            _frame = _frame[0:x, round(0.2 * y) : round(0.8 * y)]
            kernel = np.ones((20, 20), np.uint8)
            _frame = cv2.erode(_frame, kernel, cv2.BORDER_REFLECT)
            hsv = cv2.cvtColor(_frame, cv2.COLOR_BGR2HSV)
            Value.append(np.mean(hsv[:, :, 2]))
            nFrame.append(n)
        except:
            pass
    nFrame = np.linspace(0, 500, len(Value))
    Value = (Value - np.min(Value)) / np.ptp(Value)
    p = interpolate.interp1d(nFrame, Value, fill_value="extrapolate")
    reg = np.linspace(0, 500, 500)

    model = Conv1DNet()
    checkpoint_path = Path(__file__).parent.absolute().joinpath(Path('time-checkpoint.pt'))
    model.load_state_dict(torch.load(checkpoint_path))
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
