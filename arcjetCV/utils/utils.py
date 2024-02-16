import numpy as np
import cv2 as cv
import os
from sklearn.neighbors import LocalOutlierFactor
from PySide6.QtCore import Signal, QThread, Slot, QTimer


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
        window: the type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'
            flat window will produce a moving average smoothing.

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


def CLAHE_normalize(bgr,clahe):
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
    height, width, _ = image.shape

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


class WorkerThread(QThread):
    image_ready = Signal(np.ndarray)

    def __init__(self, processor, video, parent=None):
        super().__init__(parent)
        self.processor = processor
        self.video = video
        self.clahe = cv.createCLAHE(clipLimit=2.0,tileGridSize=(9,9))
        self.frame = None

        # Setup a timer to trigger sending processed image 
        self.timer = QTimer()
        self.timer.setInterval(100)
        #self.timer.timeout.connect(self.send_frame)
        

    def run(self, ilow, ihigh, skips, inputdict, opl, WRITEVIDEO):
        if WRITEVIDEO:
            self.video.get_writer()

        # Process frames
        cr = self.processor.CROP
        for frame_index in range(ilow,ihigh+1, skips):
            frame = self.video.get_frame(frame_index)

            if frame is not None:
                #Normalize input frame crop window
                try:
                    if self.processor.CHANNELS == 1:
                        crop_ = frame[cr[0][0]:cr[0][1], cr[1][0]:cr[1][1]]
                        frame[cr[0][0]:cr[0][1], cr[1][0]:cr[1][1]] = CLAHE_normalize(crop_, self.clahe)
                    else:
                        crop_ = frame[cr[0][0]:cr[0][1], cr[1][0]:cr[1][1], :]
                        frame[cr[0][0]:cr[0][1], cr[1][0]:cr[1][1], :] = CLAHE_normalize(crop_, self.clahe)
                except IndexError:
                    pass
                # Process frame
                inputdict["INDEX"] = frame_index
                contour_dict,argdict = self.processor.process(frame, inputdict)

                # Draw contours
                for key in contour_dict.keys():
                    if key == 'MODEL':
                        cv.drawContours(frame, contour_dict[key], -1, (0,255,0), 2)
                    elif key == 'SHOCK':
                        cv.drawContours(frame, contour_dict[key], -1, (0,0,255), 2)
                cv.drawContours(frame, contour_dict[key], -1, (0,0,255), 2)
                annotate_image_with_frame_number(frame, frame_index)
                argdict.update(contour_dict)
                opl.append(argdict.copy())

                # Add processed frame to video output
                if WRITEVIDEO:
                    self.video.writer.write(frame)

                self.frame = frame

        # Write output data
        opl.write()

        # close output video
        if WRITEVIDEO:
            self.video.close_writer()

        self.finished.emit()

    @Slot()
    def send_frame(self):
        rgb = cv.cvtColor(self.frame, cv.COLOR_BGR2RGB)
        self.image_ready.emit(rgb)
        print("emitted image")
