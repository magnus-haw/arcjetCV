import cv2 as cv
import numpy as np
import os, sys
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
from arcjetCV.utils.output import OutputListJSON


class ArcjetProcessor:
    """ Video frame processor
    """
    def __init__(self, videometa):
        """
        Initializes the ArcjetProcessor object.

        :param videometa: dictionary containing video metadata
        """
        self.flow_dir = videometa['FLOW_DIRECTION']
        self.h = videometa['HEIGHT']
        self.w = videometa['WIDTH']
        self.crop = videometa.crop_range()
        self.cnn = CNN()

    def update_video_meta(self, videometa):
        """
        Updates video metadata.

        :param videometa: dictionary containing updated video metadata
        """
        self.flow_dir = videometa['FLOW_DIRECTION']
        self.h = videometa['HEIGHT']
        self.w = videometa['WIDTH']
        self.crop = videometa.crop_range()
        
    def get_flow_direction(self, frame):
        """
        Infers flow direction from the provided frame.

        :param frame: opencv image
        :returns flowDirection: string, "left or "right"
        """
        if len(frame.shape) == 3:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        else:
            gray = frame

        # smooth image to remove speckles/text
        gray = cv.GaussianBlur(gray, (15, 15), 0)

        # find location of max intensity
        _, _, _, max_loc = cv.minMaxLoc(gray)
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
        Uses histogram of 8-bit grayscale image (0,255) to classify image type.

        :param frame: opencv image
        :param argdict: dictionary to store flags
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

    def segment(self, img_crop, argdict):
        """
        Segments image using one of several methods specified in argdict.

        :param img_crop: cropped opencv image
        :param argdict: dictionary containing segmentation method and related parameters
        :returns: contour_dict: dictionary containing contours
                  flags: dictionary containing flags
        """

        if argdict["SEGMENT_METHOD"] == "AutoHSV":
            contour_dict, flags = contoursAutoHSV(img_crop, flags=argdict)

        elif argdict["SEGMENT_METHOD"] == "HSV":
            try:
                HSVModelRange = argdict["HSV_MODEL_RANGE"]
                HSVShockRange = argdict["HSV_SHOCK_RANGE"]
            except KeyError:
                HSVModelRange = [(0, 0, 150), (121, 125, 255)]
                HSVShockRange = [(125, 40, 85), (170, 80, 230)]
                print(f"HSVRange not provided, using default value of HSVModelRange: {HSVModelRange}, HSVShockRange: {HSVShockRange}")
            img_clahe = clahe_normalize(img_crop)
            contour_dict, flags = contoursHSV(img_clahe, log=None, 
                                              minHSVModel=HSVModelRange[0], maxHSVModel=HSVModelRange[1], 
                                              minHSVShock=HSVShockRange[0], maxHSVShock=HSVShockRange[1])

        elif argdict["SEGMENT_METHOD"] == "GRAY":
            try:
                thresh = argdict["THRESHOLD"]
            except:
                thresh = 240
                print(f"Threshold not provided, using default value of {thresh}")
            img_clahe = clahe_normalize(img_crop)
            contour_dict, flags = contoursGRAY(img_clahe, thresh=thresh, log=None)

        elif argdict["SEGMENT_METHOD"] == "CNN":
            contour_dict, flags = contoursCNN(img_crop, self.cnn)
        
        else: return
        
        argdict.update(flags)
        return contour_dict, argdict

    def get_edges_metrics(self, contour_dict, argdict, offset):
        """
        Retrieves edges and metrics from contour dictionary.

        :param contour_dict: dictionary containing contours
        :param argdict: dictionary containing metrics
        :param offset: tuple containing offset values
        :returns: edges: dictionary containing edges
                  argdict: updated dictionary containing metrics
        """
        edges = {}
        for key in contour_dict.keys():
            c = contour_dict[key]

            if c is not None and len(c) > 0:
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
                edges[key] = getEdgeFromContour(c, self.flow_dir, offset=(self.crop[0][0] - offset[0], self.crop[1][0] - offset[1]))

                if len(edges[key]) > 0:
                    if key == "MODEL":
                        outputs = getPoints(edges[key], flow_direction=self.flow_dir, r=[-0.95, -0.50, 0, 0.50, 0.95], prefix="MODEL")
                    else:  # SHOCK
                        outputs = getPoints(edges[key], flow_direction=self.flow_dir, r=[0], prefix="SHOCK")
                    argdict.update(outputs)
            else:
                edges[key] = None
        return edges, argdict

    def make_crop_square(self, frame):
        """
        Makes the provided frame square by cropping or padding.

        :param frame: opencv image
        :returns: square_frame: square opencv image
                  offset: list containing offset values
        """
        cropped_frame = frame[self.crop[0][0]:self.crop[0][1], self.crop[1][0]:self.crop[1][1]]
        cropped_height, cropped_width = cropped_frame.shape[:2]
        square_side = max(cropped_height, cropped_width)
        square_frame = np.squeeze(np.zeros((square_side, square_side, frame.shape[2]), dtype=cropped_frame.dtype))
        start_y = (square_side - cropped_height) // 2
        start_x = (square_side - cropped_width) // 2
        square_frame[start_y:start_y + cropped_height, start_x:start_x + cropped_width] = cropped_frame
        return square_frame, [start_y, start_x]

    def process(self, frame, argdict):
        """
        Processes the given frame.

        :param frame: opencv image
        :param argdict: dictionary containing segmentation parameters
        :returns: edges: dictionary containing edges
                  argdict: updated dictionary containing metrics
        
        Example:
        ```python
        processor = ArcjetProcessor(videometa)
        frame = cv.imread('frame.jpg')
        argdict = {"SEGMENT_METHOD": "AutoHSV", "MODEL_FRACTION": 0.005}
        edges, argdict = processor.process(frame, argdict)
        ```
        """
        if self.flow_dir is None: self.flow_dir = self.get_flow_direction(frame)
        frame_crop, offset = self.make_crop_square(frame)
        argdict = self.get_image_flags(frame_crop, argdict)
        contour_dict, argdict = self.segment(frame_crop, argdict)
        edges, argdict = self.get_edges_metrics(contour_dict, argdict, offset)
        return edges, argdict.copy()

    def process_all(self, video, options, first_frame, last_frame, frame_stride, output_json='', write_video=False):
        """
        Processes all frames in the video.

        :param video: video object
        :param options: dictionary containing segmentation options
        :param first_frame: index of the first frame to process
        :param last_frame: index of the last frame to process
        :param frame_stride: stride for frame processing
        :param output_json: filename for output JSON file
        :param write_video: boolean indicating whether to write processed video

        Example:
        ```python
        video = Video('input_video.mp4')
        options = {"SEGMENT_METHOD": "AutoHSV", "MODEL_FRACTION": 0.005}
        processor = ArcjetProcessor(videometa)
        processor.process_all(video, options, 0, 100, 1, 'output.json', write_video=True)
        ```
        """

        if write_video:
            video.get_writer()

        if output_json != '':
            filename = "%s_%i_%i.json" % (output_json, first_frame, last_frame)
            out_json = OutputListJSON(os.path.join(video.folder, filename))

        # Process frames
        for frame_index in range(first_frame, last_frame + 1, frame_stride):
            frame = video.get_frame(frame_index)

            if frame is None:
                print(f"Failed at frame {frame_index}")
                return

            options["INDEX"] = frame_index
            contour_dict, argdict = self.process(frame, options)

            # Draw contours
            for key in contour_dict.keys():
                if key == "MODEL":
                    cv.drawContours(frame, contour_dict[key], -1, (0, 255, 0), 2)
                elif key == "SHOCK":
                    cv.drawContours(frame, contour_dict[key], -1, (0, 0, 255), 2)
            cv.drawContours(frame, contour_dict[key], -1, (0, 0, 255), 2)
            annotate_image_with_frame_number(frame, frame_index)
            argdict.update(contour_dict)
            
            if output_json != '':
                out_json.append(argdict.copy())

            # Add processed frame to video output
            if write_video:
                frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                video.writer.write(frame)

            sys.stdout.write(f"\rProcessing video using {options['SEGMENT_METHOD']} ... " + 
                             f"{min(((((frame_index - first_frame) / frame_stride) + 1) / 
                             np.ceil((last_frame - first_frame + 1) / frame_stride)) * 100, 100):.1f}%")
        print()

        if output_json != '':
            out_json.write()

        if write_video:
            video.close_writer()
