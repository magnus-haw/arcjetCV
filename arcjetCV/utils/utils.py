import numpy as np
import cv2 as cv
import os
from sklearn.neighbors import LocalOutlierFactor


def splitfn(fn: str):
    fn = os.path.abspath(fn)
    path, fn = os.path.split(fn)
    name, ext = os.path.splitext(fn)
    return path, name, ext


def smooth(x,window_len=11,window='hanning'):
    """smooth the data using a window with requested size.

    This method is based on the convolution of a scaled window with the signal.
    The signal is prepared by introducing reflected copies of the signal
    (with the window size) in both ends so that transient parts are minimized
    in the begining and end part of the output signal.

    input:
        x: the input signal
        window_len: the dimension of the smoothing window; should be an odd integer
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman' flat window will produce a moving average smoothing.

    output:
        the smoothed signal

    example:

    t=linspace(-2,2,0.1)
    x=sin(t)+randn(len(t))*0.1
    y=smooth(x)

    see also:

    numpy.hanning, numpy.hamming, numpy.bartlett, numpy.blackman, numpy.convolve
    scipy.signal.lfilter

    TODO: the window parameter could be the window itself if an array instead of a string
    NOTE: length(output) != length(input), to correct this: return y[(window_len/2-1):-(window_len/2)] instead of just y.
    """

    x = np.array(x)
    if x.ndim != 1:
        raise ValueError("smooth only accepts 1 dimension arrays.")

    if x.size < window_len:
        raise ValueError("Input vector needs to be bigger than window size.")


    if window_len<3:
        return x


    if not window in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError("Window is one of 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'")


    s=np.r_[x[window_len-1:0:-1],x,x[-2:-window_len-1:-1]]
    
    if window == 'flat': #moving average
        w=np.ones(window_len,'d')
    else:
        w=eval('np.'+window+'(window_len)')

    y=np.convolve(w/w.sum(),s,mode='valid')
    return y[int(window_len/2)-1:-int(window_len/2)-1]


def clahe_normalize(bgr, clahe):
    lab = cv.cvtColor(bgr, cv.COLOR_BGR2LAB)
    lab[:,:,0] = clahe.apply(lab[:,:,0])
    bgr = cv.cvtColor(lab, cv.COLOR_LAB2BGR)
    return bgr


def annotateImage(orig,flags,top=True,left=True):
    try:
        y,x,c = np.shape(orig)

        if top:
            yp = int(y*.035)
        else:
            yp = int(y*.85)
        if left:
            xp = int(x*.035)
        else:
            xp = int(y*.85)

        offset=0
        for key in ['OVEREXPOSED', 'UNDEREXPOSED']:
            if flags[key]:
                cv.putText(
                orig, #numpy array on which text is written
                "{0}: {1}".format(key,True), #text
                (xp,yp+offset), #position at which writing has to start
                cv.FONT_HERSHEY_SIMPLEX, #font family
                1, #font size
                (0, 255, 255, 255), #font color
                3) #font stroke
            offset += int(y*.035)
    except:
        print("Annotation error")


def getOutlierMask(metrics):
    X = np.nan_to_num(np.array(metrics).T)
    clf = LocalOutlierFactor(n_neighbors=11, contamination='auto')
    # use fit_predict to compute the predicted labels of the training samples
    # (when LOF is used for outlier detection, the estimator has no predict,
    # decision_function and score_samples methods).
    return clf.fit_predict(X)


def annotate_image_with_frame_number(image, frame_number):
    # Convert frame number to string
    frame_text = f"Frame: {frame_number}"

    # Get the dimensions of the image
    _, width, _ = image.shape

    # Set the font properties
    font = cv.FONT_HERSHEY_SIMPLEX
    font_scale = 0.8
    font_thickness = 2

    # Calculate the size of the frame text
    (text_width, text_height), _ = cv.getTextSize(frame_text, font, font_scale, font_thickness)

    # Calculate the position to place the frame text in the top right corner
    text_position = (width - text_width - 10, 30)

    # Draw the frame text on the image
    cv.putText(image, frame_text, text_position, font, font_scale, (0, 255, 0), font_thickness)
