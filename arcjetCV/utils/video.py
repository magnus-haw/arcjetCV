import os
import json
import cv2 as cv
import numpy as np
import threading
from arcjetCV.utils.utils import splitfn
from arcjetCV.segmentation.time.time_segmentation import (
    time_segmentation,
    extract_interest,
)


class Video(object):
    """
    Convenience wrapper for opencv video capture.

    This class provides a simple interface for working with video files using OpenCV. It encapsulates functionality for reading frames from a video file, setting the current frame, and writing processed frames to a new video file.

    Attributes:
        fpath (str): Path to the video file.
        name (str): Name of the video file.
        folder (str): Directory containing the video file.
        ext (str): Extension of the video file.
        cap: OpenCV VideoCapture object for reading video frames.
        nframes (int): Total number of frames in the video.
        fps (float): Frames per second of the video.
        shape (tuple): Shape of the video frames (height, width, channels).
        last_frame: Last frame read from the video.
        writer: OpenCV VideoWriter object for writing processed frames.
        _lock: Threading lock for thread-safe access to the video capture object.

    Example:
    ```python
    video = Video('input_video.mp4')
    print(video)
    frame = video.get_frame(0)
    ```
    """

    def __init__(self, path):
        """
        Initializes the Video object.

        :param path: path to the video file
        """
        ### path variables
        self.fpath = path
        folder, name, ext = splitfn(path)
        self.name = name
        self.folder = folder
        self.ext = ext
        self._lock = threading.Lock()

        ### opencv video file object
        self.cap = cv.VideoCapture(self.fpath)
        self.nframes = int(self.cap.get(cv.CAP_PROP_FRAME_COUNT))
        self.fps = self.cap.get(cv.CAP_PROP_FPS)
        ret, frame = self.cap.read()
        self.shape = np.shape(frame)
        self.h, self.w, self.chan = self.shape
        self.last_frame = frame
        print(f"Loaded {self.fpath} with {self.nframes} frames and shape {self.shape}")

        if self.chan not in [1, 3]:
            raise IndexError(
                "ERROR: number of channels of input video (%i) is not 1 or 3!"
                % self.chan
            )

        ### video output
        self.writer = None
        self.output_path = os.path.join(self.folder, "video_out_" + self.name + ".m4v")

    def __str__(self):
        """
        Returns a string representation of the Video object.
        """
        return "Video: {}, shape={}, nframes={}".format(
            self.fpath,
            self.shape,
            self.nframes,
        )

    def get_next_frame(self):
        """
        Retrieves the next frame from the video.

        :returns: next frame
        """
        with self._lock:
            _, self.last_frame = self.cap.read()
            return self.last_frame

    def set_frame(self, index):
        """
        Sets the frame at the specified index.

        :param index: index of the frame to set
        """
        with self._lock:
            self.cap.set(cv.CAP_PROP_POS_FRAMES, index)
            return

    def get_frame(self, index):
        """
        Retrieves the frame at the specified index.

        :param index: index of the frame to retrieve
        :returns: RGB frame at the specified index
        """
        with self._lock:
            self.cap.set(cv.CAP_PROP_POS_FRAMES, index)
            _, self.last_frame = self.cap.read()
            return cv.cvtColor(self.last_frame, cv.COLOR_BGR2RGB)

    def close(self):
        """
        Closes the video capture.
        """
        if self.writer is not None:
            self.writer.release()
        self.cap.release()

    def get_writer(self, video_output_name):
        """
        Initializes the video writer.
        """
        video_output_path = os.path.join(self.folder, video_output_name)
        vid_cod = cv.VideoWriter_fourcc("m", "p", "4", "v")
        print(f"Writing {video_output_path}")
        self.writer = cv.VideoWriter(
            video_output_path, vid_cod, self.fps, (self.shape[1], self.shape[0])
        )

    def close_writer(self):
        """
        Closes the video writer.
        """
        self.writer.release()


class VideoMeta(dict):
    """
    Subclass of dictionary designed to save/load video metadata in JSON format.

    This class extends the dictionary class to provide functionality for saving and loading video metadata in JSON format. It also includes methods for resetting frame crop parameters and setting frame crop parameters.

    Attributes:
        folder (str): Directory containing the video metadata file.
        name (str): Name of the video metadata file.
        ext (str): Extension of the video metadata file.
        path (str): Path to the video metadata file.

    Example:
    ```python
    video = Video('input_video.mp4') # load video
    video_meta = VideoMeta(video, 'metadata.json') # create/load metadata obj
    video_meta.write() # write metadata to file
    ```
    """

    def __init__(self, video, path):
        """
        Initializes the VideoMeta object.

        :param video: Video object
        :param path: path to the video file
        """
        super(VideoMeta, self).__init__()
        folder, name, ext = splitfn(path)
        self.folder = folder
        self.name = name
        self.ext = ext
        self.path = path

        ### Meta Parameters for each video
        self["WIDTH"] = None
        self["HEIGHT"] = None
        self["CHANNELS"] = None
        self["NFRAMES"] = None
        self["FIRST_GOOD_FRAME"] = None
        self["LAST_GOOD_FRAME"] = None
        self["MODELPERCENT"] = None
        self["FLOW_DIRECTION"] = None
        self["PREAMBLE_RANGE"] = None
        self["STING_VISIBLE_RANGES"] = None
        self["CROP_YMIN"] = None
        self["CROP_YMAX"] = None
        self["CROP_XMIN"] = None
        self["CROP_XMAX"] = None
        self["NOTES"] = None
        self["BRIGHTNESS"] = None

        if os.path.exists(path):
            self.load(path)
        else:
            self["WIDTH"] = video.w
            self["HEIGHT"] = video.h
            self["CHANNELS"] = video.chan
            self["NFRAMES"] = video.nframes

            try:  # Infer meta parameters
                print("Inferring first and last frames ... ", end="")
                _, out = time_segmentation(video)
                start, end = extract_interest(out)
                print("Done")
                self["FIRST_GOOD_FRAME"] = max(
                    round(start[0] * video.nframes / 500), int(video.nframes * 0.1)
                )
                self["LAST_GOOD_FRAME"] = min(
                    round(video.nframes * end[-1] / 500), int(video.nframes)
                )
            except:
                print("Time Segmentation Failed")
                self["FIRST_GOOD_FRAME"] = 0
                self["LAST_GOOD_FRAME"] = video.nframes

            # initial crop
            self.reset_frame_crop()

            print("Calculating brightness ... ", end="")
            self["BRIGHTNESS"] = []
            video.set_frame(0)
            for _ in range(video.nframes):
                ret, frame = video.cap.read()
                if not ret:
                    break
                gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                brightness = np.mean(gray_frame)
                self["BRIGHTNESS"].append(round(brightness, 2))
            print("Done")
            self.write()

    def write(self):
        """
        Writes the metadata to a JSON file.
        """
        print(f"Writing {self.path} file ... ", end="")
        fout = open(self.path, "w+")
        json.dump(self, fout)
        fout.close()
        print("Done")

    def load(self, path):
        """
        Loads metadata from a JSON file.

        :param path: path to the JSON file
        """
        fin = open(path, "r")
        dload = json.load(fin)
        self.update(dload)
        fin.close()
        print(f"Loaded {path}")

        ### Ensure path vars are correct
        folder, name, ext = splitfn(path)
        self.folder = folder
        self.name = name
        self.ext = ext
        self.path = path

    def reset_frame_crop(self):
        """
        Resets frame crop parameters to defaults.
        """
        self["CROP_YMIN"] = int(self["HEIGHT"] * 0.10)
        self["CROP_YMAX"] = int(self["HEIGHT"] * 0.90)
        self["CROP_XMIN"] = int(self["WIDTH"] * 0.10)
        self["CROP_XMAX"] = int(self["WIDTH"] * 0.90)

    def set_frame_crop(self, ymin, ymax, xmin, xmax):
        """
        Sets frame crop parameters.

        :param ymin: minimum y coordinate
        :param ymax: maximum y coordinate
        :param xmin: minimum x coordinate
        :param xmax: maximum x coordinate
        """
        self["CROP_YMIN"] = ymin
        self["CROP_YMAX"] = ymax
        self["CROP_XMIN"] = xmin
        self["CROP_XMAX"] = xmax

    def crop_range(self):
        """
        Returns the crop range.
        """
        return [
            [self["CROP_YMIN"], self["CROP_YMAX"]],
            [self["CROP_XMIN"], self["CROP_XMAX"]],
        ]
