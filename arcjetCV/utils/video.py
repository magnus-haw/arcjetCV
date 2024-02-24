import os
import json
import cv2 as cv
import numpy as np
import threading
from arcjetCV.utils.utils import splitfn
from arcjetCV.segmentation.time.time_segmentation import time_segmentation, extract_interest


class Video(object):
    ''' Convenience wrapper for opencv video capture

    Methods:
        get_frame: gets arbitrary frame
        get_next_frame: gets next frame
        get_writer: get a video writer object
        close: closes video and writer object
        close_writer: closes writer object
    '''
    def __init__(self, path):
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
        self.h,self.w,self.chan = self.shape
        self.last_frame = frame

        ### video output
        self.writer = None

    def __str__(self):
        return 'Video: {}, shape={}, nframes={}'.format(self.fpath,self.shape,self.nframes,)

    def get_next_frame(self):
        with self._lock:
            _, self.last_frame = self.cap.read()
            return self.last_frame

    def set_frame(self, index):
        with self._lock:
            self.cap.set(cv.CAP_PROP_POS_FRAMES,index)
            return

    def get_frame(self, index):
        with self._lock:
            self.cap.set(cv.CAP_PROP_POS_FRAMES,index)
            _, self.last_frame = self.cap.read()
            return cv.cvtColor(self.last_frame, cv.COLOR_BGR2RGB)

    def close(self):
        if self.writer is not None:
            self.writer.release()
        self.cap.release()

    def get_writer(self):
        vid_cod = cv.VideoWriter_fourcc('m','p','4','v')
        fname = os.path.join(self.folder,"edit_"+self.name+'.m4v')
        print(f"Writing {fname}")
        self.writer = cv.VideoWriter(fname, vid_cod, self.fps,(self.shape[1], self.shape[0]))

    def close_writer(self):
        self.writer.release()


class VideoMetaJSON(dict):
    ''' Subclass of dictionary designed to save/load video metadata in JSON format creates *.meta files with useful information'''
    def __init__(self, video, path):
        super(VideoMetaJSON, self).__init__()
        folder, name, ext = splitfn(path)
        self.folder = folder
        self.name = name
        self.ext = ext
        self.path = path

        ### Meta Parameters for each video
        self['WIDTH'] = None
        self['HEIGHT'] = None
        self['CHANNELS'] = None
        self['NFRAMES'] = None
        self['FIRST_GOOD_FRAME'] = None
        self['LAST_GOOD_FRAME'] = None
        self['MODELPERCENT'] = None
        self['FLOW_DIRECTION'] = None
        self['PREAMBLE_RANGE'] = None
        self['STING_VISIBLE_RANGES'] = None
        self['YMIN'] = None
        self['YMAX'] = None
        self['XMIN'] = None
        self['XMAX'] = None
        self['NOTES'] = None
        self['BRIGHTNESS'] = None
        
        if os.path.exists(path):
            self.load(path)
        else:
            self["WIDTH"] = video.w
            self["HEIGHT"] = video.h
            self["CHANNELS"] = 3
            self["NFRAMES"] = video.nframes
            
            try:  # Infer meta parameters
                print("Inferring first and last frames ... ", end='')
                _, out = time_segmentation(video)
                start, end = extract_interest(out)
                print("Done")
                self["FIRST_GOOD_FRAME"] = max(round(start[0] * video.nframes / 500), int(video.nframes * 0.1))
                self["LAST_GOOD_FRAME"] = min(round(video.nframes * end[-1] / 500), int(video.nframes))
            except:
                print("Time Segmentation Failed")
                self["FIRST_GOOD_FRAME"] = 0
                self["LAST_GOOD_FRAME"] = video.nframes

            # initial crop
            self["YMIN"] = 20
            self["YMAX"] = video.h
            self["XMIN"] = int(video.w * 0.10)
            self["XMAX"] = int(video.w * 0.90)
            
            print("Calculating brightness ... ", end='')
            self['BRIGHTNESS'] = []
            video.set_frame(0)
            for _ in range(video.nframes):
                ret, frame = video.cap.read()
                if not ret:
                    break
                gray_frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                brightness = np.mean(gray_frame)
                self['BRIGHTNESS'].append(round(brightness, 2))
            print("Done")
            self.write()
    
    def write(self):
        print(f"Writing {self.path} file ... ", end='')
        fout = open(self.path,'w+')
        json.dump(self, fout)
        fout.close()
        print("Done")

    def load(self,path):
        fin = open(path,'r')
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

    def crop_range(self):
        return [[self['YMIN'],self['YMAX']],[self['XMIN'], self['XMAX']]]
