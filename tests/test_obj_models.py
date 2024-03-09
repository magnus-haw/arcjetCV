import unittest
import numpy as np
from pathlib import Path
from arcjetCV.utils.video import VideoMeta
from arcjetCV.utils.output import OutputListJSON


# class TestVideoMeta(unittest.TestCase):

#     def setUp(self):
#         # Create a temporary file for testing using pathlib.Path
#         self.test_file = Path('test_video.meta')

#     def tearDown(self):
#         # Remove the temporary file after each test
#         if self.test_file.exists():
#             self.test_file.unlink()

#     def test_write_and_load(self):
#         # Create an instance of VideoMetaJSON and set some data
#         video_meta = VideoMeta(self.test_file)
#         video_meta['WIDTH'] = 1286
#         video_meta['HEIGHT'] = 720
#         video_meta['CHANNELS'] = 3
#         video_meta['NFRAMES'] = 719
#         video_meta['CROP_YMIN'] = 150
#         video_meta['CROP_YMAX'] = 600
#         video_meta['CROP_XMIN'] = 100
#         video_meta['CROP_XMAX'] = 270

#         # Write the data to the file
#         video_meta.write()

#         # Create another instance and load the data from the file
#         loaded_meta = VideoMeta(self.test_file)

#         # Check if the loaded data matches the original data
#         self.assertEqual(loaded_meta['WIDTH'], 1286)
#         self.assertEqual(loaded_meta['HEIGHT'], 720)
#         self.assertEqual(loaded_meta['CHANNELS'], 3)
#         self.assertEqual(loaded_meta['NFRAMES'], 719)
#         self.assertEqual(loaded_meta['CROP_YMIN'], 150)
#         self.assertEqual(loaded_meta['CROP_YMAX'], 600)
#         self.assertEqual(loaded_meta['CROP_XMIN'], 100)
#         self.assertEqual(loaded_meta['CROP_XMAX'], 270)

#     def test_crop_range(self):
#         # Create an instance of VideoMetaJSON and set some data
#         video_meta = VideoMeta(self.test_file)
#         video_meta['CROP_YMIN'] = 10
#         video_meta['CROP_YMAX'] = 100
#         video_meta['CROP_XMIN'] = 20
#         video_meta['CROP_XMAX'] = 200

#         # Test the crop_range method
#         expected_range = [[10, 100], [20, 200]]
#         self.assertEqual(video_meta.crop_range(), expected_range)

class TestOutputListJSON(unittest.TestCase):

    def setUp(self):
        # Create a temporary file for testing using pathlib.Path
        self.test_file = Path('test_output_000_500.json')

    def tearDown(self):
        # Remove the temporary file after each test
        if self.test_file.exists():
            self.test_file.unlink()

    def test_write_and_load(self):
        # Create an instance of OutputListJSON and add some sample data
        output_list = OutputListJSON(self.test_file)
        output_list.clear()
        output_list.extend([
            {"INDEX": 10, "DATA": "Frame 0", "numpy":np.zeros(3)},
            {"INDEX": 11, "DATA": "Frame 1"},
            {"INDEX": 12, "DATA": "Frame 2"},
        ])

        # Write the data to the file
        output_list.write()

        # Create another instance and load the data from the file
        loaded_list = OutputListJSON(self.test_file)
        loaded_list.load(self.test_file, extend=True)

        # Check if the loaded data matches the original data
        self.assertEqual(len(loaded_list), 3)
        self.assertEqual(loaded_list[0]["DATA"], "Frame 0")
        self.assertEqual(loaded_list[1]["DATA"], "Frame 1")
        self.assertEqual(loaded_list[2]["DATA"], "Frame 2")

    def test_append(self):
        # Create an instance of OutputListJSON
        output_list = OutputListJSON(self.test_file)
        output_list.clear()

        # Append some data within the specified index range
        output_list.append({"INDEX": 450, "DATA": "Frame 5"})
        output_list.append({"INDEX": 410, "DATA": "Frame 10"})

        # Append data outside the specified index range
        output_list.append({"INDEX": 2000, "DATA": "Frame 20"})

        # Check if the data was appended correctly within the range
        self.assertEqual(len(output_list), 2)
        self.assertEqual(output_list[0]["DATA"], "Frame 5")
        self.assertEqual(output_list[1]["DATA"], "Frame 10")


if __name__ == '__main__':
    unittest.main()
