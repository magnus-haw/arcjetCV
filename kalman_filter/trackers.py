"""Point-wise and shape-parameter boundary trackers.

Both trackers reduce a sequence of per-frame boundaries to a fixed-size
numeric representation, run it through :func:`~arcjetCV.segmentation.
tracking.kalman.kalman_rts_smooth`, and (for the shape-parameter tracker)
reconstruct a boundary curve from the filtered/smoothed parameters.

- :func:`track_pointwise` implements the first approach from the arcjetCV
  filtering extension: a Kalman filter + RTS smoother applied directly to
  individual boundary-point locations.
- :func:`track_shape_params` implements the second approach: the same
  filtering/smoothing framework applied to a reduced set of
  geometry-dependent shape parameters (circle fit for hemispherical
  articles, or a generic radial profile for ISO-Q / other geometries).
"""

import numpy as np

from kalman_filter.boundary import resample_polyline
from kalman_filter.kalman import kalman_rts_smooth
from kalman_filter.shape_params import (
    DEFAULT_PROFILE_R,
    extract_circle_params,
    extract_profile_params,
    reconstruct_circle_boundary,
    reconstruct_profile_boundary,
)

__all__ = ["track_pointwise", "track_shape_params"]


def _edge_xy(edge):
    """Normalize an edge (opencv (N,1,2) contour or plain (N,2) array) to
    (N, 2), or return None if the edge is missing/empty."""
    if edge is None:
        return None
    pts = np.asarray(edge, dtype=float).reshape(-1, 2)
    return pts if len(pts) > 0 else None


def track_pointwise(
    edge_sequence, n_points=61, dt=1.0, process_var=1.0, measurement_var=4.0
):
    """Point-wise Kalman filter + RTS smoother boundary tracking.

    Each frame's boundary is resampled to ``n_points`` correspondence
    points via arc-length parameterization (see
    :func:`~kalman_filter.boundary.resample_polyline`),
    then each of the resulting 2*n_points coordinate channels is tracked
    independently (but simultaneously) with a constant-velocity Kalman
    filter and RTS smoother.

    :param edge_sequence: list of length T; each element is either None
        (missing/failed segmentation for that frame) or an array-like
        ordered boundary (N, 2) or opencv-style (N, 1, 2).
    :param n_points: number of correspondence points per frame.
    :param dt: frame-to-frame time step.
    :param process_var: Kalman process-noise variance (position units^2 per
        frame^3); higher values track fast changes more but smooth less.
    :param measurement_var: Kalman measurement-noise variance (position
        units^2); higher values smooth more.
    :returns: dict with keys:
        - "raw": (T, n_points, 2) resampled (unfiltered) boundaries,
          NaN for frames with no edge.
        - "filtered": (T, n_points, 2) forward-only Kalman estimates.
        - "smoothed": (T, n_points, 2) RTS-smoothed estimates.
    """
    T = len(edge_sequence)
    raw = np.full((T, n_points, 2), np.nan)
    for t, edge in enumerate(edge_sequence):
        pts = _edge_xy(edge)
        if pts is not None:
            raw[t] = resample_polyline(pts, n_points)

    z = raw.reshape(T, n_points * 2)
    result = kalman_rts_smooth(
        z, dt=dt, process_var=process_var, measurement_var=measurement_var
    )

    return {
        "raw": raw,
        "filtered": result.filtered_pos.reshape(T, n_points, 2),
        "smoothed": result.smoothed_pos.reshape(T, n_points, 2),
    }


def track_shape_params(
    edge_sequence,
    flow_direction="right",
    geometry="hemisphere",
    r_values=DEFAULT_PROFILE_R,
    n_points=61,
    dt=1.0,
    process_var=1.0,
    measurement_var=4.0,
):
    """Shape-parameter Kalman filter + RTS smoother boundary tracking.

    Each frame's boundary is reduced to a short geometry-dependent
    parameter vector (see :mod:`kalman_filter.
    shape_params`), the parameter time series is filtered/smoothed
    channel-wise, and a boundary curve is reconstructed from the
    filtered/smoothed parameters at every frame.

    :param edge_sequence: list of length T; each element is either None
        or an opencv-style ordered boundary contour (N, 1, 2), as returned
        by :func:`~arcjetCV.segmentation.contour.contour.getEdgeFromContour`.
    :param flow_direction: "left", "right", "up", or "down".
    :param geometry: "hemisphere" (algebraic circle fit; 3 parameters:
        center_x, center_y, radius) or "profile" (generic radial profile
        sampled at ``r_values``; works for non-circular geometries such as
        ISO-Q test articles).
    :param r_values: relative offsets used by the "profile" geometry.
    :param n_points: number of points to sample along each reconstructed
        boundary.
    :param dt: frame-to-frame time step.
    :param process_var: Kalman process-noise variance.
    :param measurement_var: Kalman measurement-noise variance.
    :returns: dict with keys "raw_params", "filtered_params",
        "smoothed_params" (each (T, P)), and "raw_boundary" (template
        boundary re-sampled for reference), "filtered_boundary",
        "smoothed_boundary" (each (T, n_points, 2)).
    """
    T = len(edge_sequence)
    if geometry == "hemisphere":
        n_params = 3
        extract = extract_circle_params
    elif geometry == "profile":
        n_params = 2 + len(r_values)
        extract = lambda edge: extract_profile_params(edge, flow_direction, r_values)
    else:
        raise ValueError(f"Unknown geometry '{geometry}', expected 'hemisphere' or 'profile'")

    params = np.full((T, n_params), np.nan)
    valid_edges = [None] * T
    for t, edge in enumerate(edge_sequence):
        pts = _edge_xy(edge)
        min_pts = 3 if geometry == "hemisphere" else 1
        if pts is not None and len(pts) >= min_pts:
            params[t] = extract(pts)
            valid_edges[t] = pts

    result = kalman_rts_smooth(
        params, dt=dt, process_var=process_var, measurement_var=measurement_var
    )
    filtered_params = result.filtered_pos
    smoothed_params = result.smoothed_pos

    filtered_boundary = np.full((T, n_points, 2), np.nan)
    smoothed_boundary = np.full((T, n_points, 2), np.nan)
    raw_boundary = np.full((T, n_points, 2), np.nan)
    for t, pts in enumerate(valid_edges):
        if pts is None:
            continue
        if geometry == "hemisphere":
            filtered_boundary[t] = reconstruct_circle_boundary(
                filtered_params[t], pts, n_points
            )
            smoothed_boundary[t] = reconstruct_circle_boundary(
                smoothed_params[t], pts, n_points
            )
            raw_boundary[t] = reconstruct_circle_boundary(params[t], pts, n_points)
        else:
            filtered_boundary[t] = reconstruct_profile_boundary(
                filtered_params[t], r_values, flow_direction, n_points
            )
            smoothed_boundary[t] = reconstruct_profile_boundary(
                smoothed_params[t], r_values, flow_direction, n_points
            )
            raw_boundary[t] = reconstruct_profile_boundary(
                params[t], r_values, flow_direction, n_points
            )

    return {
        "raw_params": params,
        "filtered_params": filtered_params,
        "smoothed_params": smoothed_params,
        "raw_boundary": raw_boundary,
        "filtered_boundary": filtered_boundary,
        "smoothed_boundary": smoothed_boundary,
    }
