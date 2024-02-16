import os
import json
import cv2 as cv
import numpy as np
import threading
from arcjetCV.utils.utils import splitfn


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
            ret, self.last_frame = self.cap.read()
            return self.last_frame

    def set_frame(self,index):
        with self._lock:
            self.cap.set(cv.CAP_PROP_POS_FRAMES,index)
            return

    def get_frame(self,index):
        with self._lock:
            self.cap.set(cv.CAP_PROP_POS_FRAMES,index)
            ret, self.last_frame = self.cap.read()
            return self.last_frame

    def close(self):
        if self.writer is not None:
            self.writer.release()
        self.cap.release()

    def get_writer(self):
        vid_cod = cv.VideoWriter_fourcc('m','p','4','v')
        print(self.folder+"/edit_"+self.name+'.m4v')
        self.writer = cv.VideoWriter(os.path.join(self.folder,"edit_"+self.name+'.m4v'),
                                         vid_cod, self.fps,(self.shape[1],self.shape[0]))

    def close_writer(self):
        self.writer.release()


class VideoMeta(object):
    ''' Class designed to save/load video metadata in readable txt format
            creates *.meta files with useful information
    '''

    inttype = ['WIDTH','HEIGHT','CHANNELS','NFRAMES',
                'FIRST_GOOD_FRAME','LAST_GOOD_FRAME',
                'YMIN','YMAX','XMIN','XMAX','FRAME_NUMBER']
    floattype = ['MODELPERCENT', 'INTENSITY_THRESHOLD']
    booltype  = ['SHOCK_VISIBLE','MODEL_VISIBLE', 'OVEREXPOSED', 'UNDEREXPOSED','SATURATED']
    pointtype = []

    def __init__(self,path):
        ### File parameters
        folder, name, ext = splitfn(path)
        self.folder = folder
        self.name = name
        self.ext = ext
        self.path = path

        ### Meta Parameters for each video
        self.WIDTH =None
        self.HEIGHT =None
        self.CHANNELS = None
        self.NFRAMES = None
        self.FIRST_GOOD_FRAME = None
        self.LAST_GOOD_FRAME = None
        self.MODELPERCENT = None
        self.FLOW_DIRECTION = None
        self.YMIN = None
        self.YMAX = None
        self.XMIN = None
        self.XMAX = None
        self.NOTES = None

        if os.path.exists(path):
            self.load(path)

    def __str__(self):
        outstr = "#Property, Value\n"
        for prop, value in vars(self).items():
            if value is not None:
                outstr += prop +", "+str(value) + '\n'
            else:
                outstr += prop +", ?\n"
        return outstr

    def get_dict(self):
        d={}
        for prop, value in vars(self).items():
            if prop not in ['folder','path','ext']:
                d[prop] = value
        return d

    def write(self):
        fout = open(self.path,'w')
        fout.write(str(self))
        fout.close()

    def load(self,path):
        fin = open(path,'r')
        print(self.path)
        lines = fin.readlines()

        for i in range(1,len(lines)):
            attrs = lines[i].split(',')
            if attrs[0] in VideoMeta.inttype:
                if attrs[1].strip() == '?':
                    setattr(self,attrs[0],0)
                else:
                    setattr(self,attrs[0],int(attrs[1].strip()) )
            elif attrs[0] in VideoMeta.floattype:
                if attrs[1].strip() == '?':
                    setattr(self,attrs[0],0.)
                else:
                    setattr(self,attrs[0],float(attrs[1]) )
            elif attrs[0] in VideoMeta.booltype:
                setattr(self,attrs[0],attrs[1].strip()=="True")
            elif attrs[0] in VideoMeta.pointtype:
                attrs[2] = attrs[2].strip()
                setattr(self,attrs[0],','.join(attrs[1:]) )
            else:
                setattr(self,attrs[0],str(attrs[1].strip()) )

        ### Ensure path vars are correct
        folder, name, ext = splitfn(path)
        self.folder = folder
        self.name = name
        self.ext = ext
        self.path = path

    def crop_range(self):
        return [[self.YMIN,self.YMAX],[self.XMIN, self.XMAX]]


class FrameMeta(VideoMeta):
    ''' Stores frame metadata in text files.

    '''
    def __init__(self,path,fnumber=None,videometa=None):
        super(FrameMeta,self).__init__(path)

        if not os.path.exists(path) and videometa is not None:
            ### load video metadata
            self.load(videometa.path)
            self.FRAME_INDEX = fnumber
            self['INDEX'] = fnumber

            ### restore frame file parameters
            folder, name, ext = splitfn(path)
            self.folder = folder
            self.name = name
            self.ext = ext
            self.path = path
            

class VideoMetaJSON(dict):
    ''' Subclass of dictionary designed to save/load video metadata in JSON format
            creates *.meta files with useful information
    '''

    def __init__(self,path):
        super(VideoMetaJSON,self).__init__()
        ### File parameters
        folder, name, ext = splitfn(path)
        self.folder = folder
        self.name = name
        self.ext = ext
        self.path = path

        ### Meta Parameters for each video
        self['WIDTH'] =None
        self['HEIGHT'] =None
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

        if os.path.exists(path):
            self.load(path)

    def write(self):
        fout = open(self.path,'w+')
        json.dump(self,fout)
        fout.close()

    def load(self,path):
        print(path)
        fin = open(path,'r')
        dload = json.load(fin)
        self.update(dload)
        fin.close()

        ### Ensure path vars are correct
        folder, name, ext = splitfn(path)
        self.folder = folder
        self.name = name
        self.ext = ext
        self.path = path

    def crop_range(self):
        return [[self['YMIN'],self['YMAX']],[self['XMIN'], self['XMAX']]]
