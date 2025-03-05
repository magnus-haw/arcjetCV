# Standard imports
import numpy as np
import cv2
import matplotlib.pyplot as plt

def asym_obj_points(rows,cols):
    circles_obj_points = np.zeros(
        (rows * cols, 3), np.float32
    )
    circles_obj_points[:, :2] = np.mgrid[
        0 : rows, 0 : cols
    ].T.reshape(-1, 2)

    for col in range(1,cols,2):
        col_arr = np.arange(0,rows)
        inds = col*rows + col_arr
        for j in inds:
            circles_obj_points[j,0] += 0.5
    return circles_obj_points

rows,cols = 4,9
img_path = "/Users/mhaw/Desktop/Screenshot 2025-02-14 at 10.35.08 AM.png"
img_path = "/Users/mhaw/Desktop/IMG_3837.jpeg"
# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

########################################Blob Detector##############################################
# Setup SimpleBlobDetector parameters.
blobParams = cv2.SimpleBlobDetector_Params()

# Change thresholds
blobParams.minThreshold = 35
blobParams.maxThreshold = 185

# Filter by Area.
blobParams.filterByArea = True
blobParams.minArea = 3000
blobParams.maxArea = 15000
# blobParams.minArea = 500
# blobParams.maxArea = 3000

# Filter by Circularity
blobParams.filterByCircularity = True
blobParams.minCircularity = 0.25

# Filter by Convexity
blobParams.filterByConvexity = True
blobParams.minConvexity = 0.75

# Filter by Inertia
blobParams.filterByInertia = True
blobParams.minInertiaRatio = 0.01

# Create a detector with the parameters
blobDetector = cv2.SimpleBlobDetector_create(blobParams)
###################################################################################################

objp = asym_obj_points(rows,cols)
# print(objp)
# plt.plot(objp[:,0],objp[:,1],'bo-')
# plt.show()
###################################################################################################


# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.

img = cv2.imread(img_path, cv2.IMREAD_COLOR)
gray = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)

###################################### Image Preprocessing #########################################

# 1. Apply Gaussian Blur to reduce noise
blurred = cv2.GaussianBlur(gray, (15, 15), 0)

# 2. Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
clahe_img = clahe.apply(blurred)

# 3. Sharpening using a kernel
kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])
sharpened = cv2.filter2D(clahe_img, -1, kernel)

# Choose which preprocessed image to use for blob detection
processed_image = sharpened

###################################################################################################


keypoints = blobDetector.detect(processed_image) # Detect blobs.

# Draw detected blobs as red circles. Need to tune detector for appropriate resolution. 
im_with_keypoints = cv2.drawKeypoints(img, keypoints, np.array([]), (0,255,0), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
im_with_keypoints_gray = cv2.cvtColor(im_with_keypoints, cv2.COLOR_BGR2GRAY)
ret, corners = cv2.findCirclesGrid(gray, (rows,cols), None, 
                                   flags = (cv2.CALIB_CB_ASYMMETRIC_GRID+ cv2.CALIB_CB_CLUSTERING ),
                                   blobDetector = blobDetector)   # Find the circle grid

print(ret)
plt.imshow(im_with_keypoints)
plt.show()

if ret == True:
    objpoints.append(objp)  # Certainly, every loop objp is the same, in 3D.

    corners2 = cv2.cornerSubPix(im_with_keypoints_gray, corners, (11,11), (-1,-1), criteria)    # Refines the corner locations.
    imgpoints.append(corners2)

    # Draw and display the corners.
    im_with_keypoints = cv2.drawChessboardCorners(img, (4,9), corners2, ret)
    plt.imshow(im_with_keypoints)
    plt.show()


ret, mtx, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)

print(mtx, dist, rvecs, tvecs)
