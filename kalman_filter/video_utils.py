"""Load actual video frames aligned to the pixel coordinate system used by
arcjetCV's stored contours, so the animation can show the source footage
alongside the boundary-tracking results.

The contours in an arcjetCV output JSON (e.g. ``tests/arcjet_test_150_400.json``)
are stored in whatever pixel coordinate system they were segmented in. For
that bundled fixture, this is the full, uncropped video frame -- verified by
drawing the raw ``MODEL``/``SHOCK`` contours directly onto the corresponding
video frames and confirming they land on the sample/shock edges with no
transform needed. This module therefore loads frames as-is, with no
cropping or padding. (Note: arcjetCV's live GUI pipeline,
:meth:`arcjetCV.utils.processor.ArcjetProcessor.make_crop_square`, *can*
crop and letterbox frames to a square before segmentation -- if you're
overlaying contours produced by that pipeline with a non-default crop
instead of this bundled fixture, you'd need to reapply the same transform.)
"""

import cv2 as cv

__all__ = ["load_video_frames"]


def load_video_frames(video_path, frame_indices):
    """Return a list of RGB frames, one per index in ``frame_indices``, in
    the same pixel coordinate system as the stored MODEL/SHOCK contours.

    :param video_path: path to the source video file.
    :param frame_indices: sequence of video frame indices to load.
    :returns: list, same length as ``frame_indices``; entries are RGB
        arrays, or None for frames that couldn't be read.
    """
    cap = cv.VideoCapture(video_path)
    frames = []
    try:
        for idx in frame_indices:
            cap.set(cv.CAP_PROP_POS_FRAMES, idx)
            ok, frame = cap.read()
            frames.append(cv.cvtColor(frame, cv.COLOR_BGR2RGB) if ok else None)
    finally:
        cap.release()
    return frames
