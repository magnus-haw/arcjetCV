"""Geometry helpers for boundary tracking: arc-length resampling and circle
fitting.

Raw leading-edge contours (see
:func:`arcjetCV.segmentation.contour.contour.getEdgeFromContour`) have a
different number of points in every frame, with no point-to-point
correspondence across frames. Point-wise Kalman tracking needs a fixed-size,
correspondence-preserving representation of the boundary, which
:func:`resample_polyline` provides via arc-length parameterization.
"""

import numpy as np
from scipy.optimize import least_squares

__all__ = ["resample_polyline", "fit_circle"]


def resample_polyline(points, n_points):
    """Resample an open polyline to ``n_points`` equally spaced (by arc
    length) points, preserving its endpoints.

    :param points: array-like, shape (N, 2), ordered polyline vertices.
    :param n_points: number of output points.
    :returns: array, shape (n_points, 2).
    """
    points = np.asarray(points, dtype=float).reshape(-1, 2)
    if len(points) == 1:
        return np.repeat(points, n_points, axis=0)

    seg_lengths = np.linalg.norm(np.diff(points, axis=0), axis=1)
    cumdist = np.concatenate([[0.0], np.cumsum(seg_lengths)])
    total = cumdist[-1]
    if total == 0:
        return np.repeat(points[:1], n_points, axis=0)

    targets = np.linspace(0.0, total, n_points)
    x = np.interp(targets, cumdist, points[:, 0])
    y = np.interp(targets, cumdist, points[:, 1])
    return np.stack([x, y], axis=1)


def fit_circle(points):
    """Geometric (orthogonal-distance) least-squares circle fit.

    The leading-edge boundaries this targets are partial arcs (typically
    well under a semicircle), for which the closed-form algebraic (Kasa)
    fit is known to be systematically biased -- it minimizes algebraic
    residuals of x^2+y^2+Dx+Ey+F=0 rather than actual point-to-circle
    distance, and that bias grows as the arc gets shorter/flatter. This
    fits the algebraic circle first for a cheap initial guess, then
    refines it by minimizing the true geometric residuals
    ``|point - center| - radius`` with Levenberg-Marquardt.

    :param points: array-like, shape (N, 2).
    :returns: (cx, cy, radius)
    """
    points = np.asarray(points, dtype=float).reshape(-1, 2)
    x = points[:, 0]
    y = points[:, 1]

    # Algebraic (Kasa) fit: x^2 + y^2 + D*x + E*y + F = 0, for the initial guess.
    A = np.stack([x, y, np.ones_like(x)], axis=1)
    b = -(x**2 + y**2)
    (D, E, F), *_ = np.linalg.lstsq(A, b, rcond=None)
    cx0 = -D / 2.0
    cy0 = -E / 2.0
    radius0 = np.sqrt(max(cx0**2 + cy0**2 - F, 0.0))

    def residuals(params):
        cx, cy, radius = params
        return np.hypot(x - cx, y - cy) - radius

    result = least_squares(residuals, x0=[cx0, cy0, radius0])
    cx, cy, radius = result.x
    return cx, cy, radius
