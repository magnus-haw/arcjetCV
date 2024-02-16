import cv2 as cv
import numpy as np
import threading
from arcjetCV.segmentation.contour.contour import (contoursHSV, contoursGRAY, contoursCNN,
                                                   getEdgeFromContour, contoursAutoHSV, getPoints)
from arcjetCV.segmentation.contour.cnn import CNN


class ArcjetProcessor:
    ''' class for image processing

    Attributes:
        WIDTH (int): openCV image width
        HEIGHT (int): openCV image height
        SHAPE (tuple): openCV image shape
        CHANNELS (int): openCV number of channels (1 or 3)
        CROP (list): [[ymin,ymax],[xmin,xmax]]
        values (dict): for countours, values
        flags (dict): for errors, flags
        FLOW_DIRECTION (str): 'left' or 'right'
        FRAME: openCV image
        FRAME_CROP: cropped image
    '''
    
    def __init__(self, frame, home, crop_range=None, flow_direction=None):
        
        self._lock = threading.Lock()
        self.SHAPE = frame.shape
        self.FRAME = frame
        self.initial_dir ="ok"

        self.HEIGHT = self.SHAPE[0]
        self.WIDTH = self.SHAPE[1]
        self.values = {}
        self.flags = {}
        if len(frame.shape) == 3:
            self.CHANNELS = self.SHAPE[2]
        else:
            self.CHANNELS = 1
        if crop_range is None:
            self.CROP = [[0,self.HEIGHT], [0,self.WIDTH]]
        else:
            self.CROP = crop_range

        # Crop frame to ROI
        try:
            if self.CHANNELS == 1:
                self.FRAME_CROP = frame[self.CROP[0][0]:self.CROP[0][1], self.CROP[1][0]:self.CROP[1][1]]
            else:
                self.FRAME_CROP = frame[self.CROP[0][0]:self.CROP[0][1], self.CROP[1][0]:self.CROP[1][1], :]
        except IndexError:
            self.FRAME_CROP = [[30,self.HEIGHT-30], [50,self.WIDTH-50]]
            raise IndexError("ERROR: processor crop window %s incompatible with given frame shape %s"%(str(self.CROP),str(frame.shape)))
        
        self.homedir = home
        self._lock = threading.Lock()
        
        self.cnn = CNN()

    def autoCrop(self,frame):
        W,H, C = frame.shape
        contours, flags = contoursAutoHSV(frame)
        print('OK contours')
        if contours['SHOCK'] is not None:
            global_contours = np.array(contours['SHOCK'],contours['MODEL'], axis=0)
        else:
            contours['MODEL']
        x,y,w,h = cv.boundingRect(global_contours)
        XMIN = max(int(x - 0.1*W),0)
        XMAX = min(int(x + w + 0.1*W),W)
        YMIN  = max(int(y - 0.1*H),0)
        YMAX = min(int(y + h + 0.1*H),H)
        return XMIN, XMAX, YMIN, YMAX

    def set_crop(self,crop_range):
        ''' sets crop window range [[ymin,ymax], [xmin,xmax]] '''
        self.CROP = crop_range
        try:
            if self.CHANNELS == 1:
                self.FRAME_CROP = self.FRAME[self.CROP[0][0]:self.CROP[0][1], self.CROP[1][0]:self.CROP[1][1]]
            else:
                self.FRAME_CROP = self.FRAME[self.CROP[0][0]:self.CROP[0][1], self.CROP[1][0]:self.CROP[1][1], :]
        except IndexError:
            self.FRAME_CROP = None
            raise IndexError("ERROR: processor crop window %s incompatible with given frame shape %s"%(str(self.CROP),str(self.FRAME.shape)))

    def get_flow_direction(self, frame):
        '''infer flow direction

        :param frame: opencv image
        :returns flowDirection: string, "left or "right"
        '''

        # Check img type
        if self.CHANNELS == 3:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        elif self.CHANNELS == 1:
            gray = frame
        else:
            raise IndexError("ERROR: number of channels of input frame (%i) is not 1 or 3!"%self.CHANNELS)

        # smooth image to remove speckles/text
        gray = cv.GaussianBlur(gray, (15,15), 0)

        # find location of max intensity
        (min_val, max_val, min_loc, max_loc) = cv.minMaxLoc(gray)
        width_img, width_loc = frame.shape[1], max_loc[1]
        flux_loc = width_loc/width_img

        # Bright location generally indicates flow direction
        if flux_loc > 0.5:
            flow_direction = "left"
        elif flux_loc < 0.5:
            flow_direction = "right"

        return flow_direction

    def get_image_flags(self, frame, argdict):
        """
        Uses histogram of 8bit grayscale image (0,255) to classify image type

        :param frame: opencv image
        :returns: dictionary of flags
        """
        try:
            verbose = argdict['VERBOSE']
            modelpercent = argdict['MODEL_FRACTION']
        except KeyError:
            verbose = False; modelpercent=0.005

        ### HSV brightness value histogram
        gray_ = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray  = cv.GaussianBlur(gray_, (5, 5), 0)
        argdict['PIXEL_MIN'] = gray.min()
        argdict['PIXEL_MAX'] = gray.max()

        ### grayscale histogram
        histr = cv.calcHist( [gray], None, None, [256], (0, 256))
        imgsize = gray.size

        ### classification criteria
        modelvis = (histr[12:250]/imgsize > 0.00).sum() != 1
        modelvis *= histr[50:250].sum()/imgsize > modelpercent
        argdict['MODEL_VISIBLE'] = modelvis

        argdict['OVEREXPOSED'] =  histr[243:].sum()/imgsize > modelpercent
        argdict['UNDEREXPOSED'] =  histr[150:].sum()/imgsize < modelpercent

        return argdict

    def preprocess(self, frame, argdict):
        '''acquire flags, get flow direction'''
        # Crop image
        try:
            if self.CHANNELS == 1:
                self.FRAME_CROP = frame[self.CROP[0][0]:self.CROP[0][1], self.CROP[1][0]:self.CROP[1][1]]
            else:
                self.FRAME_CROP = frame[self.CROP[0][0]:self.CROP[0][1], self.CROP[1][0]:self.CROP[1][1], :]
        except IndexError:
            self.FRAME_CROP = None
            raise IndexError("ERROR: processor crop window %s incompatible with given frame shape %s"%(str(self.CROP),str(frame.shape)))

        # Get flow direction
        self.initial_dir = "lateral"

        if self.FLOW_DIRECTION is None:
            self.FLOW_DIRECTION = self.get_flow_direction(frame)

        # Get exposure classification
        argdict = self.get_image_flags(self.FRAME_CROP, argdict)

        return self.FRAME_CROP, argdict

    def segment(self, img_crop, argdict):
        ''' segment image using one of several methods'''
        #print(argdict["SEGMENT_METHOD"])

        if argdict["SEGMENT_METHOD"] == 'AutoHSV':
            #use contoursAutoHSV
            contour_dict, flags = contoursAutoHSV(img_crop, flags=argdict)
            argdict.update(flags)

        elif argdict["SEGMENT_METHOD"] == 'HSV':
            #use contoursHSV
            try:
                HSVModelRange = argdict["HSV_MODEL_RANGE"]
                HSVShockRange = argdict["HSV_SHOCK_RANGE"]
            except KeyError:
                HSVModelRange = [(0,0,150), (121,125,255)]
                HSVShockRange = [(125,40,85), (170,80,230)]

            contour_dict, flags = contoursHSV(img_crop,log=None,
                                        minHSVModel=HSVModelRange[0],maxHSVModel=HSVModelRange[1],
                                        minHSVShock=HSVShockRange[0],maxHSVShock=HSVShockRange[1])
            argdict.update(flags)

        elif argdict["SEGMENT_METHOD"] == 'GRAY':
            #use contoursGRAY
            try:
                thresh = argdict["THRESHOLD"]
            except:
                thresh = 240
            contour_dict, flags = contoursGRAY(img_crop,thresh=thresh,log=None)
            argdict.update(flags)

        elif argdict["SEGMENT_METHOD"] == 'CNN':
            #use machine learning CNN
            contour_dict, flags = contoursCNN(img_crop, self.cnn)
            argdict.update(flags)

        return contour_dict, argdict

    def reduce(self, contour_dict, argdict):
        ''' get edges and metrics '''
        edges = {}
        for key in contour_dict.keys():
            c = contour_dict[key]

            if c is not None:
                ### get contour area
                M = cv.moments(c)
                argdict[key+"_AREA"] = M["m00"]

                ### get centroid
                if M["m00"] > 0:
                    argdict[key+"_CENTROID_X"] = int(M["m10"] / M["m00"])
                    argdict[key+"_CENTROID_Y"] = int(M["m01"] / M["m00"])
                else:
                    argdict[key+"_CENTROID_X"] = np.nan
                    argdict[key+"_CENTROID_Y"] = np.nan

                ### get front edge
                edges[key] = getEdgeFromContour(c,self.FLOW_DIRECTION, offset =(self.CROP[0][0],self.CROP[1][0]) )

                if key == "MODEL":
                    outputs = getPoints(edges[key], flow_direction= self.FLOW_DIRECTION, r=[-.75,-.25,0,.25,.75], prefix='MODEL')
                    argdict.update(outputs)
                elif key == "SHOCK":
                    outputs = getPoints(edges[key], flow_direction= self.FLOW_DIRECTION, r=[0],prefix="SHOCK")
                    argdict.update(outputs)
            else:
                edges[key] = None
        return edges, argdict

    def process(self, frame, argdict):
        ''' fully process image '''
        with self._lock:
            try:
                frame_crop, argdict = self.preprocess(frame, argdict)
                contour_dict, argdict = self.segment(frame_crop, argdict)
                edges, argdict = self.reduce(contour_dict, argdict)
            except:
                edges = {"MODEL":None,"SHOCK":None}
            return edges, argdict.copy()
