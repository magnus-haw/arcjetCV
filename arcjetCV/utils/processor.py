import cv2 as cv
import numpy as np
import sys
from arcjetCV.segmentation.contour.contour import (
    contoursHSV,
    contoursGRAY,
    contoursCNN,
    getEdgeFromContour,
    contoursAutoHSV,
    getPoints,
)
from arcjetCV.segmentation.contour.cnn import CNN
from arcjetCV.utils.utils import clahe_normalize, annotate_image_with_frame_number


class ArcjetProcessor:
    """class for video frame processing

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
    """

    def __init__(self, frame, home, crop_range=None, flow_direction=None):
        self.SHAPE = frame.shape
        self.FRAME = frame
        self.FLOW_DIRECTION = flow_direction

        self.HEIGHT = self.SHAPE[0]
        self.WIDTH = self.SHAPE[1]
        self.values = {}
        self.flags = {}
        if len(frame.shape) == 3:
            self.CHANNELS = self.SHAPE[2]
        else:
            self.CHANNELS = 1
        if crop_range is None:
            self.CROP = [[0, self.HEIGHT], [0, self.WIDTH]]
        else:
            self.CROP = crop_range

        self.set_crop(self.CROP)

        self.homedir = home
        self.cnn = CNN()
        self.clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(9, 9))

    def set_crop(self, crop_range):
        """sets crop window range [[ymin,ymax], [xmin,xmax]]"""
        self.CROP = crop_range
        try:
            # Crop frame to ROI
            if self.CHANNELS == 1:
                self.FRAME_CROP = self.FRAME[
                    self.CROP[0][0] : self.CROP[0][1], self.CROP[1][0] : self.CROP[1][1]
                ]
            else:
                self.FRAME_CROP = self.FRAME[
                    self.CROP[0][0] : self.CROP[0][1],
                    self.CROP[1][0] : self.CROP[1][1],
                    :,
                ]

            # Determine the dimensions of self.FRAME_CROP
            cropped_height, cropped_width = self.FRAME_CROP.shape[:2]

            # Find the size of the new square frame (maximum of cropped frame's dimensions)
            square_side = max(cropped_height, cropped_width)

            # Create a new square frame filled with black pixels
            # Adjust for the number of channels
            if self.CHANNELS == 1:
                square_frame = np.zeros(
                    (square_side, square_side), dtype=self.FRAME_CROP.dtype
                )
            else:
                square_frame = np.zeros(
                    (square_side, square_side, self.CHANNELS),
                    dtype=self.FRAME_CROP.dtype,
                )

            # Calculate starting coordinates to center `self.FRAME_CROP` within `square_frame`
            start_y = (square_side - cropped_height) // 2
            start_x = (square_side - cropped_width) // 2

            # Place `self.FRAME_CROP` into `square_frame`
            if self.CHANNELS == 1:
                square_frame[
                    start_y : start_y + cropped_height,
                    start_x : start_x + cropped_width,
                ] = self.FRAME_CROP
            else:
                square_frame[
                    start_y : start_y + cropped_height,
                    start_x : start_x + cropped_width,
                    :,
                ] = self.FRAME_CROP
            # Update self.FRAME_CROP to the new square frame
            self.FRAME_CROP = square_frame

        except IndexError:
            self.FRAME_CROP = [[30, self.HEIGHT - 30], [50, self.WIDTH - 50]]
            raise IndexError(
                f"ERROR: processor crop window {self.CROP} incompatible with given frame shape {frame.shape}"
            )

    def get_flow_direction(self, frame):
        """infer flow direction

        :param frame: opencv image
        :returns flowDirection: string, "left or "right"
        """

        # Check img type
        if self.CHANNELS == 3:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        elif self.CHANNELS == 1:
            gray = frame
        else:
            raise IndexError(
                "ERROR: number of channels of input frame (%i) is not 1 or 3!"
                % self.CHANNELS
            )

        # smooth image to remove speckles/text
        gray = cv.GaussianBlur(gray, (15, 15), 0)

        # find location of max intensity
        (min_val, max_val, min_loc, max_loc) = cv.minMaxLoc(gray)
        width_img, width_loc = frame.shape[1], max_loc[1]
        flux_loc = width_loc / width_img

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
            modelpercent = argdict["MODEL_FRACTION"]
        except KeyError:
            modelpercent = 0.005

        ### HSV brightness value histogram
        gray_ = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        gray = cv.GaussianBlur(gray_, (5, 5), 0)
        argdict["PIXEL_MIN"] = gray.min()
        argdict["PIXEL_MAX"] = gray.max()

        ### grayscale histogram
        histr = cv.calcHist([gray], None, None, [256], (0, 256))
        imgsize = gray.size

        ### classification criteria
        modelvis = (histr[12:250] / imgsize > 0.00).sum() != 1
        modelvis *= histr[50:250].sum() / imgsize > modelpercent
        argdict["MODEL_VISIBLE"] = modelvis

        argdict["OVEREXPOSED"] = histr[243:].sum() / imgsize > modelpercent
        argdict["UNDEREXPOSED"] = histr[150:].sum() / imgsize < modelpercent
        return argdict

    def preprocess(self, frame, argdict):
        """acquire flags, get flow direction"""
        # Crop image
        try:
            if self.CHANNELS == 1:
                self.FRAME_CROP = frame[
                    self.CROP[0][0] : self.CROP[0][1], self.CROP[1][0] : self.CROP[1][1]
                ]
            else:
                self.FRAME_CROP = frame[
                    self.CROP[0][0] : self.CROP[0][1],
                    self.CROP[1][0] : self.CROP[1][1],
                    :,
                ]
        except IndexError:
            self.FRAME_CROP = None
            raise IndexError(
                "ERROR: processor crop window %s incompatible with given frame shape %s"
                % (str(self.CROP), str(frame.shape))
            )

        # Get flow direction
        if self.FLOW_DIRECTION is None:
            self.FLOW_DIRECTION = self.get_flow_direction(frame)

        # Get exposure classification
        argdict = self.get_image_flags(self.FRAME_CROP, argdict)

        return self.FRAME_CROP, argdict

    def segment(self, img_crop, argdict):
        """segment image using one of several methods"""

        if argdict["SEGMENT_METHOD"] == "AutoHSV":
            contour_dict, flags = contoursAutoHSV(img_crop, flags=argdict)

        elif argdict["SEGMENT_METHOD"] == "HSV":
            try:
                HSVModelRange = argdict["HSV_MODEL_RANGE"]
                HSVShockRange = argdict["HSV_SHOCK_RANGE"]
            except KeyError:
                HSVModelRange = [(0, 0, 150), (121, 125, 255)]
                HSVShockRange = [(125, 40, 85), (170, 80, 230)]

            contour_dict, flags = contoursHSV(
                img_crop,
                log=None,
                minHSVModel=HSVModelRange[0],
                maxHSVModel=HSVModelRange[1],
                minHSVShock=HSVShockRange[0],
                maxHSVShock=HSVShockRange[1],
            )

        elif argdict["SEGMENT_METHOD"] == "GRAY":
            try:
                thresh = argdict["THRESHOLD"]
            except:
                thresh = 240
            contour_dict, flags = contoursGRAY(img_crop, thresh=thresh, log=None)

        elif argdict["SEGMENT_METHOD"] == "CNN":
            contour_dict, flags = contoursCNN(img_crop, self.cnn)

        else:
            return
        argdict.update(flags)
        return contour_dict, argdict

    def reduce(self, contour_dict, argdict):
        """get edges and metrics"""
        edges = {}
        for key in contour_dict.keys():
            c = contour_dict[key]

            if c is not None:
                ### get contour area
                M = cv.moments(c)
                argdict[key + "_AREA"] = M["m00"]

                ### get centroid
                if M["m00"] > 0:
                    argdict[key + "_CENTROID_X"] = int(M["m10"] / M["m00"])
                    argdict[key + "_CENTROID_Y"] = int(M["m01"] / M["m00"])
                else:
                    argdict[key + "_CENTROID_X"] = np.nan
                    argdict[key + "_CENTROID_Y"] = np.nan

                ### get front edge
                edges[key] = getEdgeFromContour(
                    c, self.FLOW_DIRECTION, offset=(self.CROP[0][0], self.CROP[1][0])
                )

                if key == "MODEL":
                    outputs = getPoints(
                        edges[key],
                        flow_direction=self.FLOW_DIRECTION,
                        r=[-0.75, -0.25, 0, 0.25, 0.75],
                        prefix="MODEL",
                    )
                    argdict.update(outputs)
                elif key == "SHOCK":
                    outputs = getPoints(
                        edges[key],
                        flow_direction=self.FLOW_DIRECTION,
                        r=[0],
                        prefix="SHOCK",
                    )
                    argdict.update(outputs)
            else:
                edges[key] = None
        return edges, argdict

    def process(self, frame, argdict):

        if self.CHANNELS == 1:
            crop_ = frame[
                self.CROP[0][0] : self.CROP[0][1], self.CROP[1][0] : self.CROP[1][1]
            ]
            frame[
                self.CROP[0][0] : self.CROP[0][1], self.CROP[1][0] : self.CROP[1][1]
            ] = clahe_normalize(crop_, self.clahe)
        else:
            crop_ = frame[
                self.CROP[0][0] : self.CROP[0][1], self.CROP[1][0] : self.CROP[1][1]
            ]
            frame[
                self.CROP[0][0] : self.CROP[0][1], self.CROP[1][0] : self.CROP[1][1]
            ] = clahe_normalize(crop_, self.clahe)

        frame_crop, argdict = self.preprocess(frame, argdict)
        contour_dict, argdict = self.segment(frame_crop, argdict)
        edges, argdict = self.reduce(contour_dict, argdict)
        return edges, argdict.copy()

    def process_all(self, video, ilow, ihigh, skips, inputdict, opl, WRITEVIDEO):

        if WRITEVIDEO:
            video.get_writer()

        # Process frames
        for frame_index in range(ilow, ihigh + 1, skips):
            frame = video.get_frame(frame_index)

            if frame is None:
                print(f"Failed at frame {frame_index}")
                return

            inputdict["INDEX"] = frame_index
            contour_dict, argdict = self.process(frame, inputdict)

            # Draw contours
            for key in contour_dict.keys():
                if key == "MODEL":
                    cv.drawContours(frame, contour_dict[key], -1, (0, 255, 0), 2)
                elif key == "SHOCK":
                    cv.drawContours(frame, contour_dict[key], -1, (0, 0, 255), 2)
            cv.drawContours(frame, contour_dict[key], -1, (0, 0, 255), 2)
            annotate_image_with_frame_number(frame, frame_index)
            argdict.update(contour_dict)
            opl.append(argdict.copy())

            # Add processed frame to video output
            if WRITEVIDEO:
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                video.writer.write(frame)

            sys.stdout.write(
                f"\rProcessing video using {inputdict['SEGMENT_METHOD']} ... "
                + f"{min(((((frame_index - ilow) / skips) + 1) / np.ceil((ihigh - ilow + 1) / skips)) * 100, 100):.1f}%"
            )

        # Write output data
        opl.write()

        # close output video
        if WRITEVIDEO:
            video.close_writer()
