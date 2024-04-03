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
from arcjetCV.utils.video import Video


class ArcjetProcessor:
    """
    Video frame processor

    Primary image processing class: used to read in video data, extract leading edges,
    hold processed arrays, and output processed data to file.
    """

    def __init__(self, videometa):
        """
        Initializes the ArcjetProcessor object.

        :param videometa: dictionary containing video metadata
        """
        self.flow_dir = videometa["FLOW_DIRECTION"]
        self.h = videometa["HEIGHT"]
        self.w = videometa["WIDTH"]
        self.crop = videometa.crop_range()
        self.cnn = CNN()

    def update_video_meta(self, videometa):
        """
        Updates video metadata.

        :param videometa: dictionary containing updated video metadata
        """
        self.flow_dir = videometa["FLOW_DIRECTION"]
        self.h = videometa["HEIGHT"]
        self.w = videometa["WIDTH"]
        self.crop = videometa.crop_range()

    def get_flow_direction(self, frame):
        """
        Infers flow direction from the provided frame.

        :param frame: opencv image
        :returns flowDirection: string, "left or "right"
        TODO: add support for top/bottom directions
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
            # Attempt to retrieve the model fraction value from argdict, defaults to 0.005 if not found
            modelfraction = argdict["MODEL_FRACTION"]
        except KeyError:
            modelfraction = 0.005

        ### Gray value histogram
        # Convert the input image to grayscale
        gray_ = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
        # Apply Gaussian blur to the grayscale image to reduce noise for better analysis
        gray = cv.GaussianBlur(gray_, (5, 5), 0)
        # Store the minimum and maximum pixel values of the grayscale image in argdict
        argdict["PIXEL_MIN"] = gray.min()
        argdict["PIXEL_MAX"] = gray.max()

        ### grayscale histogram
        histr = cv.calcHist([gray], None, None, [256], (0, 256))
        imgsize = gray.size

        ### classification criteria

        # bright pixels occupy more than one histogram bin (not a single shade)
        modelvis = ((histr[12:250] / imgsize) > 0.00).sum() != 1
        # bright pixels exceed a threshold fraction of the full image
        modelvis *= (histr[50:250].sum() / imgsize) > modelfraction
        argdict["MODEL_VISIBLE"] = modelvis

        argdict["OVEREXPOSED"] = (histr[243:].sum() / imgsize) > modelfraction
        argdict["UNDEREXPOSED"] = histr[150:].sum() / imgsize < modelfraction
        return argdict

    def segment(self, img_crop, argdict):
        """
        Segments image using one of several methods specified in argdict.

        :param img_crop: cropped opencv image
        :param argdict: dictionary containing segmentation method and related parameters
        :returns: contour_dict: dictionary containing contours
                flags: dictionary containing flags
        """

        # Check the segmentation method specified in argdict and execute the corresponding block
        if argdict["SEGMENT_METHOD"] == "AutoHSV":
            # If the method is AutoHSV, call the contoursAutoHSV function with the cropped image
            contour_dict, flags = contoursAutoHSV(img_crop, flags=argdict)

        elif argdict["SEGMENT_METHOD"] == "HSV":
            # If the method is HSV, first try to retrieve HSV range values from argdict
            try:
                self.HSVModelRange = argdict["HSV_MODEL_RANGE"]
                self.HSVShockRange = argdict["HSV_SHOCK_RANGE"]
            except KeyError:
                # If the ranges are not specified, use default values and print a message
                self.HSVModelRange = [(0, 0, 150), (121, 125, 255)]
                self.HSVShockRange = [(125, 40, 85), (170, 80, 230)]
                print(
                    f"HSVRange not provided, using default value of self.HSVModelRange: {self.HSVModelRange}, self.HSVShockRange: {self.HSVShockRange}"
                )
            # Normalize the cropped image for better segmentation
            img_clahe = clahe_normalize(img_crop)
            # Call the contoursHSV function with the normalized image and HSV ranges
            contour_dict, flags = contoursHSV(
                img_clahe,
                log=None,
                minHSVModel=self.HSVModelRange[0],
                maxHSVModel=self.HSVModelRange[1],
                minHSVShock=self.HSVShockRange[0],
                maxHSVShock=self.HSVShockRange[1],
            )

        elif argdict["SEGMENT_METHOD"] == "GRAY":
            # If the method is GRAY, try to retrieve the threshold value from argdict
            try:
                thresh = argdict["THRESHOLD"]
            except:
                # Use a default threshold if not specified and print a message
                thresh = 240
                print(f"Threshold not provided, using default value of {thresh}")
            # Normalize the cropped image
            img_clahe = clahe_normalize(img_crop)
            # Call the contoursGRAY function with the normalized image and the threshold
            contour_dict, flags = contoursGRAY(img_clahe, thresh=thresh, log=None)

        elif argdict["SEGMENT_METHOD"] == "CNN":
            # If the method is CNN, call the contoursCNN function with the cropped image and the CNN model
            contour_dict, flags = contoursCNN(img_crop, self.cnn)

        else:
            # If none of the specified methods match, return None to indicate failure
            return

        # Update the original argdict with the flags returned from the segmentation function
        argdict.update(flags)
        # Return the dictionary of contours and the updated argdict
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
                edges[key] = getEdgeFromContour(
                    c,
                    self.flow_dir,
                    offset=(self.crop[0][0] - offset[0], self.crop[1][0] - offset[1]),
                )

                if len(edges[key]) > 0:
                    if key == "MODEL":
                        outputs = getPoints(
                            edges[key],
                            flow_direction=self.flow_dir,
                            r=[-0.95, -0.50, 0, 0.50, 0.95],
                            prefix="MODEL",
                        )
                    else:  # SHOCK
                        outputs = getPoints(
                            edges[key],
                            flow_direction=self.flow_dir,
                            r=[0],
                            prefix="SHOCK",
                        )
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
        # Crop the frame based on predefined crop coordinates stored in self.crop
        # self.crop is expected to be a tuple or list with two elements, each an (start, end) pair for y and x dimensions respectively
        cropped_frame = frame[
            self.crop[0][0] : self.crop[0][1], self.crop[1][0] : self.crop[1][1]
        ]

        # Check if the cropped frame is grayscale (i.e., has only one channel)
        if len(cropped_frame.shape) == 2 or cropped_frame.shape[2] == 1:
            # Convert grayscale to RGB
            cropped_frame = cv.cvtColor(cropped_frame, cv.COLOR_GRAY2RGB)

        # Determine the height and width of the cropped frame
        cropped_height, cropped_width = cropped_frame.shape[:2]

        # Calculate the side length of the new square frame as the max of cropped height and width
        square_side = max(cropped_height, cropped_width)

        # Initialize a square frame filled with zeros (black) of the same type as the cropped frame
        square_frame = np.zeros(
            (square_side, square_side, 3), dtype=cropped_frame.dtype
        )

        # Calculate starting points (y, x) to paste the cropped frame into the square frame
        # so that it is centered within the square frame
        start_y = (square_side - cropped_height) // 2
        start_x = (square_side - cropped_width) // 2

        # Paste the cropped frame into the square frame at the calculated starting points
        square_frame[
            start_y : start_y + cropped_height, start_x : start_x + cropped_width
        ] = cropped_frame

        # Return the square frame along with the offset values indicating where the cropped frame
        # was placed within the square frame
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
        # Determine the flow direction of the frame if not already set
        if self.flow_dir is None:
            self.flow_dir = self.get_flow_direction(frame)

        # Make the frame square to ensure consistent processing, obtaining the cropped frame and offset
        frame_crop, offset = self.make_crop_square(frame)

        # Update argdict with image flags based on the cropped frame
        argdict = self.get_image_flags(frame_crop, argdict)

        # Segment the cropped frame, updating argdict with segmentation results
        contour_dict, argdict = self.segment(frame_crop, argdict)

        # Calculate edge metrics based on contours, updating argdict further
        edges, argdict = self.get_edges_metrics(contour_dict, argdict, offset)

        # Return the edges and a copy of the updated argdict
        return edges, argdict.copy()

    def process_all(
        self,
        video: Video,
        options,
        first_frame,
        last_frame,
        frame_stride,
        output_prefix="",
        write_json=True,
        write_video=False,
        display_shock=True,
    ):
        """
        Processes all frames in the video.

        :param video: video object (defined in utils/video.py)
        :param options: dictionary containing segmentation options
        :param first_frame: index of the first frame to process
        :param last_frame: index of the last frame to process
        :param frame_stride: stride for frame processing
        :param write_json: boolean indicating whether to write processed data to JSON file
        :param write_video: boolean indicating whether to write processed video

        Example:
        ```python
        video = Video('input_video.mp4')
        options = {"SEGMENT_METHOD": "AutoHSV", "MODEL_FRACTION": 0.005}
        processor = ArcjetProcessor(videometa)
        processor.process_all(video, options, 0, 100, 1, 'output.json', write_video=True)
        ```
        """

        # Initialize video writer if write_video is True
        if write_video:

            video_output_name = "video_out_%s_%i_%i.m4v" % (
                output_prefix,
                first_frame,
                last_frame,
            )
            video.get_writer(video_output_name)

        # Setup output JSON file
        if output_prefix == "":
            output_prefix = video.name
        self.filename = "%s_%i_%i.json" % (output_prefix, first_frame, last_frame)
        out_json = OutputListJSON(os.path.join(video.folder, self.filename))

        # Iterate over frames from first_frame to last_frame, with steps of frame_stride
        for frame_index in range(first_frame, last_frame + 1, frame_stride):
            try:
                frame = video.get_frame(frame_index)

                # If a frame cannot be retrieved, print an error message and return
                if frame is None:
                    print(f"Failed at frame {frame_index}")
                    continue

                # Update options with the current frame index
                options["INDEX"] = frame_index

                # Process the current frame, obtaining contours and updated argdict
                contour_dict, argdict = self.process(frame, options)

                # Draw model and shock contours on the frame for visualization
                color_map = {
                    "MODEL": (0, 255, 0),
                    "SHOCK": (255, 0, 255),
                }  # Define colors for MODEL and SHOCK

                if display_shock:
                    for key, contours in contour_dict.items():
                        cv.drawContours(
                            frame, contours, -1, color_map.get(key, (255, 0, 255)), 2
                        )
                else:
                    # Draw only the MODEL contours if display_shock is False
                    cv.drawContours(
                        frame, contour_dict["MODEL"], -1, color_map["MODEL"], 2
                    )

                # Annotate the frame with its index for reference
                annotate_image_with_frame_number(frame, frame_index)
                argdict.update(contour_dict)

                # update output dictionary
                out_json.append(argdict.copy())

                # Add processed frame to video output
                if write_video:
                    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
                    video.writer.write(frame)

                # Print processing progress
                sys.stdout.write(
                    f"\rProcessing video using {options['SEGMENT_METHOD']} ... "
                    + f"{min(((((frame_index - first_frame) / frame_stride) + 1) / np.ceil((last_frame - first_frame + 1) / frame_stride)) * 100, 100):.1f}%"
                )
            except Exception as e:
                print(f"Failed at frame {frame_index} with error:\n" + str(e))

        if write_json:
            out_json.write()

        if write_video:
            video.close_writer()

        return out_json
