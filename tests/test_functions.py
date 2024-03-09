import os
import unittest
import numpy as np
from arcjetCV.utils.utils import splitfn
from arcjetCV.segmentation.contour.contour import filter_hsv_ranges, getPoints


class TestSplitFn(unittest.TestCase):

    def test_splitfn(self):
        # Test with a standard path
        path, name, ext = splitfn("/user/documents/file.txt")
        self.assertEqual(path, os.path.abspath("/user/documents"))
        self.assertEqual(name, "file")
        self.assertEqual(ext, ".txt")
        
        # Test with no extension
        path, name, ext = splitfn("/user/documents/file")
        self.assertEqual(path, os.path.abspath("/user/documents"))
        self.assertEqual(name, "file")
        self.assertEqual(ext, "")

        # Test with multiple dots in filename
        path, name, ext = splitfn("/user/documents/file.part1.txt")
        self.assertEqual(path, os.path.abspath("/user/documents"))
        self.assertEqual(name, "file.part1")
        self.assertEqual(ext, ".txt")

        # Test with relative path
        path, name, ext = splitfn("documents/file.txt")
        expected_path = os.path.abspath("documents")
        self.assertEqual(path, expected_path)
        self.assertEqual(name, "file")
        self.assertEqual(ext, ".txt")

class TestFilterHsvRanges(unittest.TestCase):

    def setUp(self):
        # Create a simple mock HSV image: 100x100, with a gradient in the hue channel
        self.hsv_image = np.zeros((100, 100, 3), dtype=np.uint8)
        self.hsv_image[:, :, 0] = np.linspace(0, 100, 100, endpoint=False).reshape(-1, 1)  # H gradient
        self.hsv_image[:, :, 1] = 128  # S constant
        self.hsv_image[:, :, 2] = 128  # V constant

    def test_filter_hsv_ranges(self):
        # Define a simple range: 50<H<100, 0<S<255, 0<V<255
        mask = filter_hsv_ranges(self.hsv_image, ([ [50, 0, 0] ], [ [100, 255, 255] ]))

        # Check the output mask: white in the specified range, black elsewhere
        for i in range(100):
            j=50
            if 50 <= i < 100:
                self.assertEqual(mask[i, j], 255)  # White
            else:
                self.assertEqual(mask[i, j], 0)    # Black

        # Test with multiple ranges
        mask_multi = filter_hsv_ranges(self.hsv_image, ([ [10, 0, 0], [95, 0, 0] ], [ [20, 255, 255], [85, 255, 255] ]))
        for i in range(100):
            j=50
            if 10 <= i <= 20 or 95 <= i <= 85:
                self.assertEqual(mask_multi[i, j], 255)  # White
            else:
                self.assertEqual(mask_multi[i, j], 0)    # Black

class TestGetPoints(unittest.TestCase):
    
    def test_right_flow(self):
        # Mock contour for flow_direction="right"
        contour = np.array([[[10, 10]], [[10, 15]], [[10, 20]], [[10, 25]], [[10, 30]]])
        result = getPoints(contour, flow_direction="right")
        
        # Asserting on some expected results. You should adapt these based on your expectations.
        self.assertEqual(result["MODEL_YCENTER"], 20)
        self.assertEqual(result["MODEL_YLOW"], 10)
        self.assertEqual(result["MODEL_CROP_YMAX"], 30)
        self.assertEqual(result["MODEL_RADIUS"], 10)
        self.assertEqual(len(result["MODEL_INTERP_XPOS"]), 5)
    
    def test_left_flow(self):
        # Mock contour for flow_direction="left"
        contour = np.array([[[5, 10]], [[5, 15]], [[5, 20]], [[5, 25]], [[5, 30]]])
        result = getPoints(contour, flow_direction="left")
        
        # Asserting on some expected results
        self.assertEqual(result["MODEL_YCENTER"], 20)
        self.assertEqual(result["MODEL_YLOW"], 10)
        self.assertEqual(result["MODEL_CROP_YMAX"], 30)
        self.assertEqual(result["MODEL_RADIUS"], 10)
        self.assertEqual(len(result["MODEL_INTERP_XPOS"]), 5)
    
    def test_up_flow(self):
        # Mock contour for flow_direction="up"
        contour = np.array([[[10, 5]], [[15, 5]], [[20, 5]], [[25, 5]], [[30, 5]]])
        result = getPoints(contour, flow_direction="up")
        
        # Asserting on some expected results
        self.assertEqual(result["MODEL_YCENTER"], 20)
        self.assertEqual(result["MODEL_YLOW"], 10)
        self.assertEqual(result["MODEL_CROP_YMAX"], 30)
        self.assertEqual(result["MODEL_RADIUS"], 10)
        self.assertEqual(len(result["MODEL_INTERP_XPOS"]), 5)
    
    def test_down_flow(self):
        # Mock contour for flow_direction="down"
        contour = np.array([[[10, 10]], [[15, 10]], [[20, 10]], [[25, 10]], [[30, 10]]])
        result = getPoints(contour, flow_direction="down")
        
        # Asserting on some expected results
        self.assertEqual(result["MODEL_YCENTER"], 20)
        self.assertEqual(result["MODEL_YLOW"], 10)
        self.assertEqual(result["MODEL_CROP_YMAX"], 30)
        self.assertEqual(result["MODEL_RADIUS"], 10)
        self.assertEqual(len(result["MODEL_INTERP_XPOS"]), 5)


if __name__ == "__main__":
    unittest.main()
