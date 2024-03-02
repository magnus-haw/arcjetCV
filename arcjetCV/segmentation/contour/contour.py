import numpy as np
import cv2 as cv


def filter_hsv_ranges(hsv: np.ndarray, ranges) -> np.ndarray:
    """
    Filter an HSV image using multiple hue-saturation-value (HSV) ranges and return the combined mask.

    The function applies multiple HSV range filters to the input image and combines the results
    using a bitwise OR operation to create a single mask that captures all the specified ranges.

    Args:
        hsv (np.ndarray): Input HSV image.
        ranges (tuple of two lists of lists): A tuple containing two lists.
            The first list contains the lower bounds of multiple HSV ranges,
            and the second list contains the upper bounds for those same ranges.
            Each bound in the lists is itself a list or tuple of three values (H, S, V).
            The number of range pairs (lower and upper bounds) can vary.

    Returns:
        np.ndarray: A combined binary mask where pixels falling within any of the provided
            HSV ranges are set to 255 (white), and all others are set to 0 (black).

    Examples:
        >>> filter_hsv_ranges(hsv_image, ([ [0, 50, 50], [20, 100, 100] ], [ [10, 255, 255], [30, 150, 150] ]))
        # Returns a mask where only the pixels in two ranges are white:
        # 1) 0<H<10, 50<S<255, 50<V<255
        # 2) 20<H<30, 100<S<150, 100<V<150

    """

    # Initialize a black mask with the same dimensions as the input image
    maskHSV = np.zeros((hsv.shape[0], hsv.shape[1]), dtype=np.uint8)

    # Iterate over each HSV range and apply the filtering
    for i in range(len(ranges[0])):
        # Convert lower and upper bounds to numpy arrays
        lower_bound = np.array(ranges[0][i], dtype=np.uint8)
        upper_bound = np.array(ranges[1][i], dtype=np.uint8)

        mask = cv.inRange(hsv, lower_bound, upper_bound)

        # Combine the current mask with the accumulated mask using bitwise OR
        maskHSV = cv.bitwise_or(mask, maskHSV)

    return maskHSV


def getEdgeFromContour(c, flow_direction, offset=None):
    """
    Find the leading edge of a contour for a given flow direction

    :param c: opencv contour, shape(n,1,n)
    :param flow_direction: 'left', 'right', 'up', or 'down'
    :returns: frontedge, contour of front edge
    """
    ### contours are oriented counterclockwise from top left

    if flow_direction == "right":
        ymin_ind = c[:, 0, 1].argmin()
        ymax_ind = c[:, 0, 1].argmax()
        frontedge = c[ymin_ind:ymax_ind, :, :]
    elif flow_direction == "left":
        ymax_ind = c[:, 0, 1].argmax()
        frontedge = c[ymax_ind:, :, :]
    elif flow_direction == "up":
        xmin_ind = c[:, 0, 0].argmin()
        xmax_ind = c[:, 0, 0].argmax()
        frontedge = c[xmin_ind:xmax_ind:, :, :]
    else:
        xmin_ind = c[:, 0, 0].argmin()
        xmax_ind = c[:, 0, 0].argmax()
        frontedge = np.append(c[xmax_ind:, :, :], c[0:xmin_ind, :, :], axis=0)

    frontedge[:, 0, 1] += offset[0]
    frontedge[:, 0, 0] += offset[1]

    return frontedge


def getPoints(c, flow_direction="right", r=[-0.95, -0.50, 0, 0.50, 0.95], prefix="MODEL"):
    """
    Given an OpenCV contour, this function returns interpolated points at specified
    relative vertical positions to the center of the contour.

    Assumptions:
    1. Only the leading edge is passed into the function (not a closed contour).
    2. The contour is dense, meaning every vertical pixel is occupied.

    Parameters:
    :param c: An OpenCV contour of shape (n, 1, n).
    :param flow_direction (str): Indicates the direction of the flow. Acceptable values
                                 are "right", "left", "up", or "down". Default is "right".
    :param r (list): A list of interpolation points relative to the contour's radius.
                     Default is [-0.95, -0.50, 0, 0.50, 0.95].
    :param prefix (str): A prefix string for keys in the output dictionary. Default is "MODEL".

    Returns:
    :return: A dictionary containing:
        - [prefix]+'_R': List of relative interpolation points.
        - [prefix]+'_YCENTER': Y-coordinate of the center of the contour.
        - [prefix]+'_YLOW': Minimum Y-coordinate of the contour.
        - [prefix]+'_CROP_YMAX': Maximum Y-coordinate of the contour.
        - [prefix]+'_RADIUS': Radius (half of the height) of the contour.
        - [prefix]+'_INTERP_XPOS': Interpolated X-coordinates corresponding to each point in 'r'.
    """

    if flow_direction in ["right", "left"]:
        ### Extract min/max ypos
        low_ind = c[:, 0, 1].argmin()
        ymin = c[low_ind, 0, 1]
        high_ind = c[:, 0, 1].argmax()
        ymax = c[high_ind, 0, 1]
        center = int((ymin + ymax) / 2)
        radius = int((ymax - ymin) / 2)

        ### Setup output dictionary
        output = {
            prefix + "_R": r,
            prefix + "_YCENTER": center,
            prefix + "_YLOW": ymin,
            prefix + "_CROP_YMAX": ymax,
            prefix + "_RADIUS": radius,
        }

        # Interpolate corresponding horizontal positions
        xpos = np.zeros(len(r))
        ypos = [int(y * radius + center) for y in r]

        li = min(low_ind, high_ind)
        hi = max(low_ind, high_ind)
        inds = np.arange(li, hi)
        for ind in inds:
            for j in range(0, len(ypos)):
                if abs(c[ind, 0, 1] - ypos[j]) < 3:
                    xpos[j] = c[ind, 0, 0]
        output[prefix + "_INTERP_XPOS"] = xpos
    else:
        ### Extract min/max ypos
        low_ind = c[:, 0, 0].argmin()
        xmin = c[low_ind, 0, 0]
        high_ind = c[:, 0, 0].argmax()
        xmax = c[high_ind, 0, 0]
        center = int((xmin + xmax) / 2)
        radius = int((xmax - xmin) / 2)

        ### Setup output dictionary
        output = {
            prefix + "_R": r,
            prefix + "_YCENTER": center,
            prefix + "_YLOW": xmin,
            prefix + "_CROP_YMAX": xmax,
            prefix + "_RADIUS": radius,
        }

        # Interpolate corresponding horizontal positions
        ypos = np.zeros(len(r))
        xpos = [int(y * radius + center) for y in r]

        li = min(low_ind, high_ind)
        hi = max(low_ind, high_ind)
        inds = np.arange(li, hi)
        for ind in inds:
            for j in range(0, len(xpos)):
                if abs(c[ind, 0, 0] - xpos[j]) < 3:
                    ypos[j] = c[ind, 0, 1]
        output[prefix + "_INTERP_XPOS"] = ypos

    return output.copy()


def contoursAutoHSV(orig, log=None, flags={"UNDEREXPOSED": False}):
    """
    Find contours using default union of multiple HSV ranges.
    Uses the BGR-HSV transformation to increase contrast.

    :param orig: opencv 8bit BGR image
    :param flags: dictionary with flags
    :param log: log object
    :returns: model contour, shock contour, flags
    """

    img = cv.cvtColor(orig, cv.COLOR_BGR2HSV)

    ### HSV pixel ranges for models taken from sample frames
    model_ranges = np.array([[(0, 0, 208), (155, 0, 155), (13, 20, 101), (0, 190, 100), (12, 150, 130)],
                             [(180, 70, 255), (165, 125, 255), (33, 165, 255), (13, 245, 160), (25, 200, 250)]])
    dim_model = np.array([[(7, 0, 8)], [(20, 185, 101)]])

    ### HSV pixel ranges for shocks taken from sample frames
    shock_ranges = np.array([[(125, 78, 115)], [(145, 190, 230)]])
    dim_shocks = np.array([[(125, 100, 35), (140, 30, 20), (118, 135, 30)], 
                           [(165, 165, 150), (156, 90, 220), (128, 194, 125)]])

    # Append additional ranges for underexposed images
    if flags["UNDEREXPOSED"]:
        model_ranges = np.hstack((model_ranges, dim_model))

    # Apply shock filter and extract shock contour
    shockfilter = filter_hsv_ranges(img, shock_ranges)
    if shockfilter.sum() < 500:
        flags["DIM_SHOCK"] = True
        shock_ranges = np.hstack((shock_ranges, dim_shocks))
        shockfilter = filter_hsv_ranges(img, shock_ranges)
    shockcontours, _ = cv.findContours(shockfilter, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # find the biggest shock contour (shockC) by area
    if len(shockcontours) == 0:
        shockC = None
        flags["SHOCK_CONTOUR_FAILED"] = True
        if log is not None:
            log.write("no shock contours found")
    else:
        shockC = max(shockcontours, key=cv.contourArea)

    # Apply model filter and extract model contour
    modelfilter = filter_hsv_ranges(img, model_ranges)
    if flags["UNDEREXPOSED"]:
        kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE, (5, 5))
        modelfilter = cv.morphologyEx(modelfilter, cv.MORPH_OPEN, kernel)
    modelcontours, _ = cv.findContours(modelfilter, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # find the biggest model contour (modelC) by area
    if len(modelcontours) == 0:
        modelC = None
        flags["MODEL_CONTOUR_FAILED"] = True
        if log is not None:
            log.write("no model contours found")
    else:
        modelC = max(modelcontours, key=cv.contourArea)

    contour_dict = {"MODEL": modelC, "SHOCK": shockC}

    return contour_dict, flags


def contoursHSV(orig, log=None, minHSVModel=(0, 0, 150), maxHSVModel=(181, 125, 256), minHSVShock=(125, 78, 115), maxHSVShock=(145, 190, 230)):
    """
    Find contours using HSV ranges image.
    Uses the BGR-HSV transformation to increase contrast.

    :param orig: opencv 8bit BGR image
    :param minHSVModel: minimum tuple for HSV range
    :param maxHSVModel: maximum tuple for HSV range
    :param minHSVShock: minimum tuple for HSV range
    :param maxHSVShock: maximum tuple for HSV range
    :returns: model contour, shock contour
    """

    flags = {"MODEL_CONTOUR_FAILED": False, "SHOCK_CONTOUR_FAILED": False}
    # Load an color image in HSV, apply HSV transform again
    hsv_ = cv.cvtColor(orig, cv.COLOR_BGR2HSV)
    hsv = cv.GaussianBlur(hsv_, (5, 5), 0)

    ### Model contours
    modelmask = cv.inRange(hsv, minHSVModel, maxHSVModel)
    modelcontours, _ = cv.findContours(modelmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # find the biggest model contour (modelC) by area
    if len(modelcontours) == 0:
        modelC = None
        flags["MODEL_CONTOUR_FAILED"] = True
        if log is not None:
            log.write("no shock contours found")
    else:
        modelC = max(modelcontours, key=cv.contourArea)

    ### Shock contours
    shockmask = cv.inRange(hsv, minHSVShock, maxHSVShock)
    shockcontours, _ = cv.findContours(shockmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # find the biggest shock contour (shockC) by area
    if len(shockcontours) == 0:
        shockC = None
        flags["SHOCK_CONTOUR_FAILED"] = True
        if log is not None:
            log.write("no shock contours found")
    else:
        shockC = max(shockcontours, key=cv.contourArea)

    contour_dict = {"MODEL": modelC, "SHOCK": shockC}

    return contour_dict, flags


def contoursGRAY(orig, thresh=150, log=None):
    """
    Detects contours in potentially overexposed images using a global grayscale threshold.

    This function first converts the input image to grayscale and then applies a binary threshold
    to isolate potentially overexposed regions. The function then detects and returns the largest contour
    found, if any, based on the area. In the event no contours are detected, the function logs the failure
    if a logging object is provided.

    Parameters:
    :param orig: An OpenCV BGR image (8-bit depth). This is typically an image that may contain
                 overexposed regions where contours need to be identified.
    :param thresh: Integer value to apply as a threshold for binary segmentation. Defaults to 150.
                   Regions with grayscale values greater than this threshold will be considered as potential contour areas.
    :param log: An optional logging object with a `write` method to capture any logging messages.
                Especially useful to track when contour detection fails. Default is None.

    Returns:
    :return: A tuple containing:
             - `contour_dict`: Dictionary with keys "MODEL" and "SHOCK".
               "MODEL" will contain the largest detected contour or None if not found.
               "SHOCK" is currently always set to None.
             - `flags`: Dictionary indicating success or failure of contour detection.
               Contains keys "SHOCK_CONTOUR_FAILED" (always set to True)
               and "MODEL_CONTOUR_FAILED" (set to True if contour detection fails).

    Example:
        img = cv.imread('overexposed_image.jpg')
        contours, flags = contoursGRAY(img)
        if not flags['MODEL_CONTOUR_FAILED']:
            cv.drawContours(img, [contours['MODEL']], -1, (0, 255, 0), 2)
            cv.imshow('Detected Contour', img)
            cv.waitKey(0)
    """
    flags = {"SHOCK_CONTOUR_FAILED": True, "MODEL_CONTOUR_FAILED": True}
    ### take channel with least saturation
    gray_ = cv.cvtColor(orig, cv.COLOR_BGR2GRAY)

    ### Global grayscale threshold
    gray = cv.GaussianBlur(gray_, (5, 5), 0)
    _, th1 = cv.threshold(gray, thresh, 255, cv.THRESH_BINARY)
    contours, _ = cv.findContours(th1, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)
    if len(contours) != 0:
        # find the biggest contour (c) by the area
        modelC = max(contours, key=cv.contourArea)
        flags["MODEL_CONTOUR_FAILED"] = False
    else:
        if log is not None:
            log.write("no GRAY model contours found at thresh==%i" % thresh)
        modelC = None
        flags["MODEL_CONTOUR_FAILED"] = True

    contour_dict = {"MODEL": modelC, "SHOCK": None}

    return contour_dict, flags


def contoursCNN(orig, model, log=None):
    """
    Find contours using HSV ranges image.
    Uses the BGR-HSV transformation to increase contrast.

    :param orig: opencv 8bit BGR image
    :param model: compiled CNN model
    :returns: model contour, shock contour
    """

    flags = {"MODEL_CONTOUR_FAILED": False, "SHOCK_CONTOUR_FAILED": False}

    ### Apply CNN
    cnnmask = model.predict(orig)

    ### Model contours
    modelmask = (((cnnmask == 1) | (cnnmask == 3)) * 255).astype(np.uint8)
    modelcontours, _ = cv.findContours(modelmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # find the biggest model contour (modelC) by area
    if len(modelcontours) == 0:
        modelC = None
        flags["MODEL_CONTOUR_FAILED"] = True
        if log is not None:
            log.write("no shock contours found")
    else:
        modelC = max(modelcontours, key=cv.contourArea)

    ### Shock contours
    shockmask = ((cnnmask == 2) * 255).astype(np.uint8)
    shockcontours, _ = cv.findContours(shockmask, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_NONE)

    # find the biggest shock contour (shockC) by area
    if len(shockcontours) == 0:
        shockC = None
        flags["SHOCK_CONTOUR_FAILED"] = True
        if log is not None:
            log.write("no shock contours found")
    else:
        shockC = max(shockcontours, key=cv.contourArea)

    contour_dict = {"MODEL": modelC, "SHOCK": shockC}

    return contour_dict, flags
