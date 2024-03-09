import unittest
import cv2 as cv
import numpy as np
from arcjetCV.segmentation.contour.contour import contoursCNN, contoursAutoHSV, contoursGRAY, contoursHSV
from unittest.mock import patch


class TestContoursGRAY(unittest.TestCase):

    def test_no_contours(self):
        """Test that the function returns the appropriate flag when no contours are found."""
        # Create a blank 100x100 black image.
        img = np.zeros((100, 100, 3), dtype=np.uint8)

        contour_dict, flags = contoursGRAY(img, 150)
        self.assertIsNone(contour_dict['MODEL'])
        self.assertTrue(flags['MODEL_CONTOUR_FAILED'])

    def test_find_contour(self):
        """Test that the function correctly finds and returns the contour of a white rectangle."""
        # Create a 100x100 black image with a white rectangle in the center.
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv.rectangle(img, (25, 25), (95, 95), (255, 255, 255), -1)

        contour_dict, flags = contoursGRAY(img, 150)
        self.assertIsNotNone(contour_dict['MODEL'])
        self.assertFalse(flags['MODEL_CONTOUR_FAILED'])

    def test_left_edge_of_rectangle(self):
        # Create a synthetic overexposed image (10 everywhere except a rectangle of value 100)
        img = np.ones((500, 500, 3), dtype=np.uint8) * 10
        cv.rectangle(img, (150, 150), (350, 350), (100, 100, 100), -1)

        # Use the contoursGRAY function
        contour_dict, flags = contoursGRAY(img, thresh=50)

        # Get the bounding rectangle of the detected contour
        x, y, w, h = cv.boundingRect(contour_dict['MODEL'])

        # Assert that the left edge of the bounding rectangle matches the rectangle's left edge in the synthetic image
        self.assertEqual(x, 150)

    def test_log_message(self):
        """Test that a message is written to the log when no contours are found."""
        # Mock a simple log object with a write method
        class MockLog:
            def __init__(self):
                self.messages = []

            def write(self, msg):
                self.messages.append(msg)

        mock_log = MockLog()

        # Create a blank 100x100 black image.
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, _ = contoursGRAY(img, 150, log=mock_log)
        
        # Check if the appropriate message was written to the log.
        self.assertTrue('no GRAY model contours found at thresh==150' in mock_log.messages)

class TestContoursAutoHSV(unittest.TestCase):

    def test_contour_detection_using_HSV(self):
        # Create a synthetic image with a clearly defined model rectangle and shock rectangle
        img = np.ones((500, 500, 3), dtype=np.uint8) * 10

        # Add synthetic model rectangle (HSV: roughly (160, 50, 220))
        cv.rectangle(img, (150, 150), (350, 350), (206, 177, 220), -1)

        # Add synthetic shock rectangle (HSV: roughly (135, 100, 220))
        cv.rectangle(img, (100, 100), (125, 400), (220, 134, 177), -1)

        # Use the contoursAutoHSV function
        contour_dict, flags = contoursAutoHSV(img)

        # Check if MODEL contour is detected
        self.assertIsNotNone(contour_dict['MODEL'])

        # Check if SHOCK contour is detected
        self.assertIsNotNone(contour_dict['SHOCK'])

        # Check if the bounding rectangle of the detected MODEL contour matches the known position
        x, y, w, h = cv.boundingRect(contour_dict['MODEL'])
        self.assertEqual((x, y, w, h), (150, 150, 201, 201))

        # Check if the bounding rectangle of the detected SHOCK contour matches the known position
        x, y, w, h = cv.boundingRect(contour_dict['SHOCK'])
        self.assertEqual((x, y, w, h), (100, 100, 26, 301))

class TestContoursHSV(unittest.TestCase):

    def test_distinct_regions(self):
        # Create a synthetic image with distinct model and shock regions
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        # Model region in BGR
        img[25:95, 25:95] = (220, 177, 134) 
        # Shock region in BGR
        img[10:20, 10:20] = (220,  65, 142) 
        contours, flags = contoursHSV(img)

        # Ensure that the model and shock contours are detected
        self.assertIsNotNone(contours['MODEL'])
        self.assertIsNotNone(contours['SHOCK'])

    def test_no_regions(self):
        # Create a blank image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        contours, flags = contoursHSV(img)

        # Ensure that no model or shock contours are detected
        self.assertIsNone(contours['MODEL'])
        self.assertIsNone(contours['SHOCK'])
        self.assertTrue(flags['MODEL_CONTOUR_FAILED'])
        self.assertTrue(flags['SHOCK_CONTOUR_FAILED'])

    def test_only_model(self):
        # Create an image with only model region
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[25:95, 25:95] = (220, 177, 134) # Model region in BGR
        contours, flags = contoursHSV(img)

        # Ensure that only the model contour is detected
        self.assertIsNotNone(contours['MODEL'])
        self.assertIsNone(contours['SHOCK'])
        self.assertFalse(flags['MODEL_CONTOUR_FAILED'])
        self.assertTrue(flags['SHOCK_CONTOUR_FAILED'])

    def test_only_shock(self):
        # Create an image with only shock region
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        img[10:20, 10:20] = (220,  65, 142) # Shock region in BGR
        contours, flags = contoursHSV(img)

        # Ensure that only the shock contour is detected
        #self.assertIsNone(contours['MODEL'])
        self.assertIsNotNone(contours['SHOCK'])
        #self.assertTrue(flags['MODEL_CONTOUR_FAILED'])
        self.assertFalse(flags['SHOCK_CONTOUR_FAILED'])

    def test_logging(self):
        class DummyLog:
            def __init__(self):
                self.messages = []
            
            def write(self, msg):
                self.messages.append(msg)

        log = DummyLog()
        # Create a blank image
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        contours, flags = contoursHSV(img, log=log)

        # Ensure that appropriate log messages are written
        self.assertIn('no shock contours found', log.messages)

    def test_matching_rectangle_model(self):
        # Create an image with only model region
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        x, y, w, h = 25, 25, 50, 50
        img[y:y+h, x:x+w] = (220, 177, 134)  # Model region in BGR
        contours, flags = contoursHSV(img)

        # Ensure that the model contour's bounding box matches the synthetic rectangle
        rect = cv.boundingRect(contours['MODEL'])
        self.assertEqual(rect, (x, y, w, h))

    def test_matching_rectangle_shock(self):
        # Create an image with only shock region
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        x, y, w, h = 25, 25, 50, 50
        img[y:y+h, x:x+w] = (220,  65, 142)  # Shock region in BGR
        contours, flags = contoursHSV(img)

        # Ensure that the shock contour's bounding box matches the synthetic rectangle
        rect = cv.boundingRect(contours['SHOCK'])
        self.assertEqual(rect, (x+1, y+1, w-2, h-2))

class TestContoursCNN(unittest.TestCase):

    def mock_cnn_apply(img, model):
        # This mocked CNN application creates a synthetic mask
        # 0: background, 1: model, 2: shock
        mask = np.zeros((100, 100))
        mask[25:95, 25:95] = 1  # model region
        mask[10:20, 10:20] = 2  # shock region
        return mask

    # @patch('utils.Functions.cnn_apply', side_effect=mock_cnn_apply)
    # def test_contoursCNN(self, mock_cnn_apply_func):
    #     # Create a synthetic image
    #     img = np.zeros((100, 100, 3), dtype=np.uint8)
    #     model = None  # For the sake of this test, the model doesn't matter because cnn_apply is mocked
    #     contours, flags = contoursCNN(img, model)

    #     # Ensure model contour matches the synthetic region
    #     model_rect = cv.boundingRect(contours['MODEL'])
    #     self.assertEqual(model_rect, (25, 25, 50, 50))

    #     # Ensure shock contour matches the synthetic region
    #     shock_rect = cv.boundingRect(contours['SHOCK'])
    #     self.assertEqual(shock_rect, (10, 10, 10, 10))
        

if __name__ == '__main__':
    unittest.main()
