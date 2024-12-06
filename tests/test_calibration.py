import unittest, cv2
from arcjetCV.utils.processor import CalibrationProcessor
from pathlib import Path

FOLDER = Path(__file__).resolve().parent

# Images
TEST_CALIB_IMG = FOLDER / "test_data/IHF405_top_view_cal.png"
SAMPLE_CALIB_PATTERN = FOLDER / "test_data/sample_calibration_pattern.png"

class TestCalibration(unittest.TestCase):
    
    def test_calibration(self):
        cp = CalibrationProcessor(rows=9, cols=4)
        cp.calibrate_intrinsics([TEST_CALIB_IMG])
        img = cv2.imread(TEST_CALIB_IMG)
        cp.get_orientation(img)

        
class TestBlobDetection(unittest.TestCase):

    def test_blob_detection1(self):
        
        image = cv2.imread(TEST_CALIB_IMG)

        # Set up the parameters for the SimpleBlobDetector
        params = cv2.SimpleBlobDetector_Params()

        # Filter by area
        params.filterByArea = True
        params.minArea = 200
        params.maxArea = 4000

        # Filter by circularity
        params.filterByCircularity = True
        params.minCircularity = 0.5

        # Filter by convexity
        params.filterByConvexity = True
        params.minConvexity = 0.8

        # Filter by inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.5

        # Create the detector
        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs
        keypoints = detector.detect(image)
        self.assertEqual(len(keypoints),36)

        # Draw detected blobs as red circles
        # im_with_keypoints = cv2.drawKeypoints(image, keypoints, np.array([]), (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        # 
        # Show the image
        # cv2.imshow("Blobs", im_with_keypoints)
        # cv2.waitKey(0)

    def test_blob_detection2(self):
        
        image = cv2.imread(SAMPLE_CALIB_PATTERN)

        # Set up the parameters for the SimpleBlobDetector
        params = cv2.SimpleBlobDetector_Params()

        # Filter by area
        params.filterByArea = True
        params.minArea = 200
        params.maxArea = 4000

        # Filter by circularity
        params.filterByCircularity = True
        params.minCircularity = 0.5

        # Filter by convexity
        params.filterByConvexity = True
        params.minConvexity = 0.8

        # Filter by inertia
        params.filterByInertia = True
        params.minInertiaRatio = 0.5

        # Create the detector
        detector = cv2.SimpleBlobDetector_create(params)

        # Detect blobs
        keypoints = detector.detect(image)
        self.assertEqual(len(keypoints),44)