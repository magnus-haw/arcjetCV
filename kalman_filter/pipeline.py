"""Standalone post-processing entry point: apply Kalman/RTS boundary
tracking to arcjetCV's per-frame segmentation output.

This does not touch the live video-processing pipeline
(:class:`arcjetCV.utils.processor.ArcjetProcessor`) or the GUI; it consumes
the contours already written to an arcjetCV output JSON file (the same
format produced by ``ArcjetProcessor.process_all``/``ProcessorWorker``,
e.g. ``tests/arcjet_test_150_400.json``) and reproduces both filtering
approaches for the sample ("MODEL") and shock ("SHOCK") boundaries.
"""

import json

import numpy as np

from arcjetCV.segmentation.contour.contour import getEdgeFromContour
from kalman_filter.trackers import track_pointwise, track_shape_params

__all__ = ["load_frames", "extract_edge_sequence", "track_boundaries"]


def load_frames(json_path):
    """Load an arcjetCV output JSON file (list of per-frame dicts)."""
    with open(json_path, "r") as f:
        return json.load(f)


def extract_edge_sequence(frames, key, flow_direction):
    """Extract the ordered leading-edge boundary for ``key`` ("MODEL" or
    "SHOCK") from each frame's raw contour.

    :param frames: list of per-frame dicts, as returned by
        :func:`load_frames`.
    :param key: "MODEL" or "SHOCK".
    :param flow_direction: "left", "right", "up", or "down".
    :returns: (edges, frame_indices) where edges is a list of length
        len(frames), each element an opencv-style (N, 1, 2) contour array
        or None for frames with no detected contour, and frame_indices is
        the corresponding list of INDEX values.
    """
    edges = []
    frame_indices = []
    for frame in frames:
        frame_indices.append(frame.get("INDEX"))
        contour = frame.get(key)
        if not contour:
            edges.append(None)
            continue
        c = np.array(contour, dtype=np.int32).reshape(-1, 1, 2)
        edge = getEdgeFromContour(c, flow_direction, offset=(0, 0))
        edges.append(edge if len(edge) > 0 else None)
    return edges, frame_indices


def track_boundaries(
    json_path,
    key="MODEL",
    flow_direction="right",
    geometry="hemisphere",
    n_points=61,
    r_values=None,
    process_var=1.0,
    measurement_var=4.0,
):
    """Load an arcjetCV output JSON and run both boundary-tracking
    approaches on the requested boundary ("MODEL" or "SHOCK").

    :param json_path: path to an arcjetCV output JSON file.
    :param key: "MODEL" (sample) or "SHOCK".
    :param flow_direction: "left", "right", "up", or "down" -- must match
        how the video was processed.
    :param geometry: shape-parameter geometry, "hemisphere" or "profile"
        (see :func:`~kalman_filter.trackers.
        track_shape_params`). Use "profile" for non-circular geometries
        such as ISO-Q test articles, or for the shock boundary.
    :param n_points: number of points per reconstructed/resampled boundary.
    :param r_values: relative offsets for the "profile" geometry; defaults
        to :data:`~kalman_filter.shape_params.DEFAULT_PROFILE_R`.
    :param process_var: Kalman process-noise variance, shared by both
        tracking approaches.
    :param measurement_var: Kalman measurement-noise variance, shared by
        both tracking approaches.
    :returns: dict with "frame_indices", "edges" (raw extracted boundaries),
        "pointwise" (output of :func:`track_pointwise`), and "shape"
        (output of :func:`track_shape_params`).
    """
    from kalman_filter.shape_params import DEFAULT_PROFILE_R

    if r_values is None:
        r_values = DEFAULT_PROFILE_R

    frames = load_frames(json_path)
    edges, frame_indices = extract_edge_sequence(frames, key, flow_direction)

    pointwise = track_pointwise(
        edges,
        n_points=n_points,
        process_var=process_var,
        measurement_var=measurement_var,
    )
    shape = track_shape_params(
        edges,
        flow_direction=flow_direction,
        geometry=geometry,
        r_values=r_values,
        n_points=n_points,
        process_var=process_var,
        measurement_var=measurement_var,
    )

    return {
        "frame_indices": frame_indices,
        "edges": edges,
        "pointwise": pointwise,
        "shape": shape,
    }
