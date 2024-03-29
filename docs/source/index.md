# arcjetCV Documentation

```{toctree} 
:caption: Quick Start
:maxdepth: 2
placeholders/readme.md
```

```{toctree} 
:caption: User Manual
:maxdepth: 2
user_manual/user_manual.md
```

## Python API

```python
# Simple example use of arcjetCV's API for batch processing 
import arcjetCV as arcv
import os

path = "/path/to/video/"
filename = "video"
filepath = os.path.join(path, filename)

video = arcv.Video(filepath + ".mp4")
videometa = arcv.VideoMeta(video, filepath + ".meta")
videometa["FLOW_DIRECTION"] = "right"
videometa.set_frame_crop(250, 780, 490, 1020)
outputprefix = "output"

processor = arcv.ArcjetProcessor(videometa)
output = processor.process_all(
    video, 
    options={"SEGMENT_METHOD": "CNN"}, 
    first_frame=videometa["FIRST_GOOD_FRAME"], 
    last_frame=videometa["LAST_GOOD_FRAME"], 
    frame_stride = 10,
    write_json = True,
    write_video = True
)

# output_data_path = output.path
# video_output_path = video.output_path
# videometa_filepath = videometa.path

```

### Functions and Classes

```{toctree} 
:maxdepth: 2
placeholders/api.md
```
