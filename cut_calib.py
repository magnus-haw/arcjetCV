import cv2
import numpy as np
import glob
import os

# === Parameters ===
chessboard_size = (5, 7)        # number of inner corners (rows, cols)
square_size_mm = 10.0           # checker size in mm
image_dir = '/Users/alexandrequintart/Downloads/Unknown.png'           # folder containing calibration images
output_dir = '/Users/alexandrequintart/Downloads'          # where to save undistorted images
os.makedirs(output_dir, exist_ok=True)

# === Prepare object points (3D points in real world)
objp = np.zeros((chessboard_size[0]*chessboard_size[1], 3), np.float32)
objp[:, :2] = np.mgrid[0:chessboard_size[0], 0:chessboard_size[1]].T.reshape(-1, 2)
objp *= square_size_mm

objpoints = []  # 3D real-world points
imgpoints = []  # 2D image points

# === Load images
images = glob.glob(os.path.join(image_dir, '*.jpg'))

for fname in images:
    img = cv2.imread(fname)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, corners = cv2.findChessboardCorners(gray, chessboard_size, None)

    if ret:
        corners2 = cv2.cornerSubPix(
            gray, corners, (11, 11), (-1, -1),
            (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        )
        objpoints.append(objp)
        imgpoints.append(corners2)
    else:
        print(f"⚠️ Chessboard not found in {fname}")

# === Camera calibration
ret, K, dist, rvecs, tvecs = cv2.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)
print("✅ Camera calibrated")
print("Camera matrix:\n", K)
print("Distortion:\n", dist)

# === Undistort and apply homography to the first image
img = cv2.imread(images[0])
h, w = img.shape[:2]

# Undistortion
new_K, roi = cv2.getOptimalNewCameraMatrix(K, dist, (w, h), 1, (w, h))
undistorted = cv2.undistort(img, K, dist, None, new_K)
cv2.imwrite(os.path.join(output_dir, "undistorted.jpg"), undistorted)

# === Homography: warp the chessboard plane to be fronto-parallel
# Use the first detected chessboard corners
img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
found, corners = cv2.findChessboardCorners(img_gray, chessboard_size)

if found:
    # Real-world points (Z=0)
    obj_pts = objp[:, :2].astype(np.float32)

    # Image points
    img_pts = corners.reshape(-1, 2)

    # Compute homography
    H, _ = cv2.findHomography(img_pts, obj_pts)
    print("Homography:\n", H)

    warped = cv2.warpPerspective(img, H, (w, h))
    cv2.imwrite(os.path.join(output_dir, "rectified.jpg"), warped)
    print("✅ Undistorted and rectified image saved.")
else:
    print("⚠️ Could not detect chessboard in the selected image for homography.")