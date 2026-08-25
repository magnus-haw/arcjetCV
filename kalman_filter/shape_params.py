"""Geometry-dependent shape-parameter extraction and boundary reconstruction.

Two parameterizations are provided, matching the two test-article families
arcjetCV targets:

- ``"circle"``: (center_x, center_y, radius) from an algebraic circle fit.
  Appropriate for hemispherical test articles, whose leading-edge boundary
  is close to a circular arc.
- ``"profile"``: (primary-axis center, primary-axis radius, interpolated
  secondary-axis positions at a handful of relative radii). This reuses
  arcjetCV's existing :func:`~arcjetCV.segmentation.contour.contour.getPoints`
  sampling convention, so it makes no circularity assumption and applies to
  any geometry, including ISO-Q test articles.

In both cases, a per-frame boundary is reduced to a short parameter vector;
:mod:`kalman_filter.trackers` runs the Kalman/RTS filter on
the parameter time series, and the ``reconstruct_*`` functions turn a
filtered/smoothed parameter vector back into a boundary curve.
"""

import numpy as np
from scipy.interpolate import PchipInterpolator

from arcjetCV.segmentation.contour.contour import getPoints

__all__ = [
    "extract_circle_params",
    "reconstruct_circle_boundary",
    "extract_profile_params",
    "reconstruct_profile_boundary",
    "DEFAULT_PROFILE_R",
]

DEFAULT_PROFILE_R = [-0.9, -0.7, -0.5, -0.25, 0.0, 0.25, 0.5, 0.7, 0.9]


def extract_circle_params(edge_points):
    """Reduce a boundary to (center_x, center_y, radius) via a circle fit.

    :param edge_points: array-like, shape (N, 2) or (N, 1, 2).
    :returns: array, shape (3,) -> [cx, cy, radius].
    """
    from kalman_filter.boundary import fit_circle

    pts = np.asarray(edge_points, dtype=float).reshape(-1, 2)
    cx, cy, radius = fit_circle(pts)
    return np.array([cx, cy, radius])


def reconstruct_circle_boundary(params, template_edge_points, n_points=61):
    """Rebuild a circular-arc boundary from filtered/smoothed circle params.

    The angular span of the arc is taken from ``template_edge_points`` (the
    raw boundary for that frame), so the reconstruction covers the same
    portion of the test article, just constrained to lie on the
    (filtered) circle instead of the noisy raw points.

    :param params: array-like, shape (3,) -> [cx, cy, radius].
    :param template_edge_points: array-like, shape (N, 2) or (N, 1, 2),
        ordered boundary points from the same frame, used only to determine
        the angular extent of the reconstructed arc.
    :param n_points: number of points to sample along the arc.
    :returns: array, shape (n_points, 2).
    """
    cx, cy, radius = params
    pts = np.asarray(template_edge_points, dtype=float).reshape(-1, 2)

    theta = np.unwrap(np.arctan2(pts[:, 1] - cy, pts[:, 0] - cx))
    theta_grid = np.linspace(theta[0], theta[-1], n_points)

    x = cx + radius * np.cos(theta_grid)
    y = cy + radius * np.sin(theta_grid)
    return np.stack([x, y], axis=1)


def extract_profile_params(edge_points, flow_direction, r_values=DEFAULT_PROFILE_R):
    """Reduce a boundary to [center, radius, interpolated positions...].

    Wraps :func:`arcjetCV.segmentation.contour.contour.getPoints`, which
    computes, along the axis perpendicular to the flow direction, the
    center and radius of the boundary and interpolates its position at
    relative offsets ``r_values`` from that center.

    :param edge_points: opencv-style contour array, shape (N, 1, 2), as
        returned by :func:`getEdgeFromContour`.
    :param flow_direction: "left", "right", "up", or "down".
    :param r_values: relative offsets (fractions of the radius) at which to
        sample the boundary.
    :returns: array, shape (2 + len(r_values),) ->
        [center, radius, interp_1, ..., interp_k].
    """
    c = np.asarray(edge_points, dtype=np.int32).reshape(-1, 1, 2)
    out = getPoints(c, flow_direction=flow_direction, r=list(r_values), prefix="P")
    center = out["P_YCENTER"]
    radius = out["P_RADIUS"]
    interp = np.asarray(out["P_INTERP_XPOS"], dtype=float)
    return np.concatenate([[float(center), float(radius)], interp])


def reconstruct_profile_boundary(params, r_values, flow_direction, n_points=61):
    """Rebuild a boundary curve from filtered/smoothed profile parameters.

    A monotone cubic (PCHIP) spline is fit through the (relative-offset,
    interpolated-position) anchor points and evaluated on a dense grid
    spanning the full [-1, 1] relative range, then mapped back to
    (center, radius) to produce absolute image coordinates.

    :param params: array-like, shape (2 + len(r_values),) ->
        [center, radius, interp_1, ..., interp_k].
    :param r_values: the relative offsets used at extraction time.
    :param flow_direction: "left", "right", "up", or "down"; determines
        whether the interpolated axis is x (secondary) vs y (primary) or
        the reverse.
    :param n_points: number of points to sample along the reconstructed
        boundary.
    :returns: array, shape (n_points, 2) -> [x, y] in image coordinates.
    """
    params = np.asarray(params, dtype=float)
    center, radius = params[0], params[1]
    interp = params[2:]
    r_values = np.asarray(r_values, dtype=float)

    order = np.argsort(r_values)
    spline = PchipInterpolator(r_values[order], interp[order], extrapolate=True)

    r_grid = np.linspace(r_values.min(), r_values.max(), n_points)
    primary = center + r_grid * radius
    secondary = spline(r_grid)

    if flow_direction in ("left", "right"):
        # getPoints interpolates x as a function of y for left/right flow.
        return np.stack([secondary, primary], axis=1)
    # getPoints interpolates y as a function of x for up/down flow.
    return np.stack([primary, secondary], axis=1)
