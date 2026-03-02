# API & CLI

## Launch the GUI
```bash
arcjetCV
```

## Minimal Python example
```python
import arcjetCV as arcv

# Load a video for processing
video = arcv.Video("tests/arcjet_test.mp4")

# You can access frames, apply filters, and write your own batch routines
for frame in video.frames[::100]:
    # Replace with your own processing pipeline
    pass
```

The Python API mirrors the GUI workflow: ingest a video, configure calibration/filters, extract edges, and export processed data. See the source modules under `arcjetCV/` for detailed implementations of calibration, filtering, and analysis tools.

## Tips
- Activate the same environment you use for the GUI before running scripts.
- Long videos benefit from a GPU build of the environment (`env/arcjetCV_env_gpu.yml`).
- If you extend the API, add new examples here so they appear in the wiki.
