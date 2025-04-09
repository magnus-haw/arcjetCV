import numpy as np
import cv2 as cv
import os
from sklearn.neighbors import LocalOutlierFactor


def splitfn(fn: str):
    """
    Splits the given file path into directory, file name, and extension.

    :param fn: file path
    :return: directory path, file name, extension
    """
    fn = os.path.abspath(fn)
    path, fn = os.path.split(fn)
    name, ext = os.path.splitext(fn)
    return path, name, ext


def smooth(x, window_len=11, window="hanning"):
    """
    Smooths the data using a window with the requested size.

    :param x: the input signal
    :param window_len: the dimension of the smoothing window; should be an odd integer
    :param window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
                   flat window will produce a moving average smoothing.
    :return: the smoothed signal

    Example:
    ```python
    t = np.linspace(-2, 2, 0.1)
    x = np.sin(t) + np.random.randn(len(t)) * 0.1
    y = smooth(x)
    ```
    """

    x = np.array(x)
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")

    if window_len < 3:
        return x

    if not window in ["flat", "hanning", "hamming", "bartlett", "blackman"]:
        raise ValueError(
            "Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'"
        )

    s = np.r_[x[window_len - 1 : 0 : -1], x, x[-2 : -window_len - 1 : -1]]

    if window == "flat":  # moving average
        w = np.ones(window_len, "d")
    else:
        w = eval("np." + window + "(window_len)")

    y = np.convolve(w / w.sum(), s, mode="valid")
    return y[int(window_len / 2) - 1 : -int(window_len / 2) - 1]


def clahe_normalize(bgr):
    """
    Applies Contrast Limited Adaptive Histogram Equalization (CLAHE) normalization to the given BGR image.

    :param bgr: BGR image
    :return: normalized BGR image
    """
    lab = cv.cvtColor(bgr, cv.COLOR_BGR2LAB)
    lab[:, :, 0] = cv.createCLAHE(clipLimit=2.0, tileGridSize=(9, 9)).apply(
        lab[:, :, 0]
    )
    bgr = cv.cvtColor(lab, cv.COLOR_LAB2BGR)
    return bgr


def annotateImage(orig, flags, top=True, left=True):
    """
    Annotates the original image with flags indicating overexposure and underexposure.

    :param orig: original image
    :param flags: dictionary of flags indicating overexposure and underexposure
    :param top: boolean, whether to annotate on the top of the image
    :param left: boolean, whether to annotate on the left side of the image
    """

    try:
        y, x, _ = np.shape(orig)

        # Adjust vertical position based on 'top' argument
        if top:
            yp = int(y * 0.035)  # Place text near the top
        else:
            yp = int(y * 0.85)  # Place text near the bottom

        # Adjust horizontal position based on 'left' argument
        if left:
            xp = int(x * 0.035)  # Place text near the left
        else:
            xp = int(x * 0.85)  # Place text near the right

        # Calculate the font properties based on the image width and height
        font_scale = max(0.5, x / 2000)  # Scale font size to ensure readability
        font_thickness = max(1, x // 1000)  # Scale thickness based on image width
        offset = 0

        # Loop through flags and annotate if True
        for key in ["OVEREXPOSED", "UNDEREXPOSED"]:
            if flags.get(key, False):
                # Ensure text is within bounds of the image
                text = f"{key}: {True}"
                (text_width, text_height), _ = cv.getTextSize(
                    text, cv.FONT_HERSHEY_SIMPLEX, font_scale, font_thickness
                )

                # Adjust position if the text goes beyond the image boundaries
                if yp + offset + text_height > y:
                    yp = y - text_height - 10  # Keep text within bottom bounds

                if xp + text_width > x:
                    xp = x - text_width - 10  # Keep text within right bounds

                # Draw text on the image
                cv.putText(
                    orig,  # numpy array on which text is written
                    text,  # text
                    (xp, yp + offset),  # position at which writing has to start
                    cv.FONT_HERSHEY_SIMPLEX,  # font family
                    font_scale,  # font size
                    (0, 255, 255),  # font color (yellow in BGR)
                    font_thickness,  # font stroke
                )
            offset += int(y * 0.035)
    except Exception as e:
        print(f"Annotation error: {e}")


def getOutlierMask(metrics):
    """
    Computes the outlier mask using Local Outlier Factor (LOF).

    :param metrics: metrics data
    :return: outlier mask
    """

    X = np.nan_to_num(np.array(metrics).T)
    clf = LocalOutlierFactor(n_neighbors=9, contamination="auto")
    # use fit_predict to compute the predicted labels of the training samples
    # (when LOF is used for outlier detection, the estimator has no predict,
    # decision_function and score_samples methods).
    return clf.fit_predict(X)


def annotate_image_with_frame_number(image, frame_number):
    """
    Annotates the given image with the frame number.

    :param image: image to annotate
    :param frame_number: frame number to annotate
    """

    # Convert frame number to string
    frame_text = f"Frame: {frame_number}"

    # Get the dimensions of the image
    height, width, _ = image.shape

    # Set the font properties
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = max(
        1, width / 1000
    )  # Scale font size to ensure readability for different image sizes
    font_thickness = max(1, width // 200)  # Scale thickness based on image width

    # Calculate the size of the frame text
    (text_width, text_height), _ = cv.getTextSize(
        frame_text, font, font_scale, font_thickness
    )

    # Calculate the position to place the frame text in the top right corner
    # Ensuring the text is within the image's height
    vertical_position = max(
        20, text_height + 10
    )  # Minimum distance from top to avoid clipping
    text_position = (width - text_width - 10, vertical_position)

    # Draw the frame text on the image
    cv.putText(
        image, frame_text, text_position, font, font_scale, (0, 255, 0), font_thickness
    )
