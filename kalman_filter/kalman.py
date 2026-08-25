"""Constant-velocity Kalman filter with Rauch-Tung-Striebel (RTS) smoothing.

This module implements the point-wise and shape-parameter boundary tracking
described in the arcjetCV filtering extension: a per-channel Kalman filter
[Kalman, 1960] is run forward over a sequence of noisy scalar measurements,
followed by an RTS backward smoothing pass [Rauch, Tung & Striebel, 1965].

The same routine is reused for both tracking approaches:
  - point-wise: each channel is one coordinate (x or y) of one boundary point
  - shape-parameter: each channel is one geometry-dependent shape parameter

All channels share the same constant-velocity dynamics (state = [position,
velocity]) and are advanced together, vectorized over the channel axis, so a
single call handles an arbitrary number of independently-tracked signals.
"""

import numpy as np

__all__ = ["KalmanRTSResult", "kalman_rts_smooth"]


class KalmanRTSResult:
    """Container for the outputs of :func:`kalman_rts_smooth`.

    Arrays are shaped (T, C) for positions/velocities and (T, C, 2, 2) for
    covariances, where T is the number of frames and C the number of
    independently-tracked channels.
    """

    def __init__(
        self,
        filtered_pos,
        filtered_vel,
        smoothed_pos,
        smoothed_vel,
        filtered_cov,
        smoothed_cov,
    ):
        self.filtered_pos = filtered_pos
        self.filtered_vel = filtered_vel
        self.smoothed_pos = smoothed_pos
        self.smoothed_vel = smoothed_vel
        self.filtered_cov = filtered_cov
        self.smoothed_cov = smoothed_cov


def kalman_rts_smooth(
    z,
    dt=1.0,
    process_var=1.0,
    measurement_var=4.0,
    initial_pos=None,
    initial_vel=0.0,
    initial_var=1.0e4,
):
    """Run a constant-velocity Kalman filter + RTS smoother over C channels.

    :param z: array, shape (T, C) or (T,). Measurements per frame per channel.
        Use ``np.nan`` for a missing measurement at a given (frame, channel);
        the filter falls back to a pure time-update (prediction only) for
        that entry, which lets tracking continue through dropped/failed
        segmentation frames.
    :param dt: time step between frames (frame index units by default).
    :param process_var: scalar or (C,) array, acceleration process-noise
        variance (larger = trust the measurements more, smooth less).
    :param measurement_var: scalar or (C,) array, measurement noise variance
        (larger = trust the model more, smooth more).
    :param initial_pos: (C,) initial position estimate; defaults to the
        first finite measurement of each channel.
    :param initial_vel: scalar or (C,) initial velocity estimate.
    :param initial_var: scalar initial state variance (large = uninformative
        prior).
    :returns: :class:`KalmanRTSResult` with filtered (forward-only) and
        smoothed (RTS, uses the full sequence) position/velocity estimates.
    """
    z = np.asarray(z, dtype=float)
    if z.ndim == 1:
        z = z[:, None]
    T, C = z.shape

    process_var = np.broadcast_to(np.asarray(process_var, dtype=float), (C,))
    measurement_var = np.broadcast_to(np.asarray(measurement_var, dtype=float), (C,))

    # Discrete white-noise-acceleration process noise for state [pos, vel].
    Q = np.zeros((C, 2, 2))
    Q[:, 0, 0] = dt**4 / 4.0 * process_var
    Q[:, 0, 1] = Q[:, 1, 0] = dt**3 / 2.0 * process_var
    Q[:, 1, 1] = dt**2 * process_var

    F = np.array([[1.0, dt], [0.0, 1.0]])
    H = np.array([1.0, 0.0])

    if initial_pos is None:
        first_valid = np.full(C, np.nan)
        for c in range(C):
            finite = z[:, c][np.isfinite(z[:, c])]
            if finite.size:
                first_valid[c] = finite[0]
        initial_pos = np.nan_to_num(first_valid, nan=0.0)
    else:
        initial_pos = np.broadcast_to(np.asarray(initial_pos, dtype=float), (C,))
    initial_vel = np.broadcast_to(np.asarray(initial_vel, dtype=float), (C,))

    x = np.stack([initial_pos, initial_vel], axis=1)  # (C, 2)
    P = np.tile(np.eye(2) * initial_var, (C, 1, 1))  # (C, 2, 2)

    filtered_pos = np.empty((T, C))
    filtered_vel = np.empty((T, C))
    filtered_cov = np.empty((T, C, 2, 2))
    # Predicted (a priori) states, needed by the RTS backward pass.
    pred_x = np.empty((T, C, 2))
    pred_P = np.empty((T, C, 2, 2))

    for t in range(T):
        # --- time update (predict) ---
        x = x @ F.T
        P = F @ P @ F.T + Q
        pred_x[t] = x
        pred_P[t] = P

        # --- measurement update ---
        valid = np.isfinite(z[t])
        if np.any(valid):
            y = z[t] - x @ H  # innovation, (C,)
            S = P[:, 0, 0] + measurement_var  # H P H^T + R, (C,)
            K = P[:, :, 0] / S[:, None]  # Kalman gain, (C, 2)

            x_upd = x + K * y[:, None]
            I_KH = np.tile(np.eye(2), (C, 1, 1))
            I_KH[:, :, 0] -= K
            P_upd = I_KH @ P

            x = np.where(valid[:, None], x_upd, x)
            P = np.where(valid[:, None, None], P_upd, P)

        filtered_pos[t] = x[:, 0]
        filtered_vel[t] = x[:, 1]
        filtered_cov[t] = P

    # --- RTS backward smoothing pass ---
    smoothed_pos = filtered_pos.copy()
    smoothed_vel = filtered_vel.copy()
    smoothed_cov = filtered_cov.copy()

    x_next_smooth = np.stack([smoothed_pos[-1], smoothed_vel[-1]], axis=1)
    P_next_smooth = smoothed_cov[-1]

    for t in range(T - 2, -1, -1):
        x_filt_t = np.stack([filtered_pos[t], filtered_vel[t]], axis=1)
        P_filt_t = filtered_cov[t]

        # Predicted state at t+1 given filtered state at t.
        x_pred = pred_x[t + 1]
        P_pred = pred_P[t + 1]

        # Smoother gain: C_t = P_t F^T (P_pred_{t+1})^{-1}
        P_pred_inv = np.linalg.inv(P_pred)
        Cgain = P_filt_t @ F.T @ P_pred_inv  # (C, 2, 2)

        diff_x = x_next_smooth - x_pred  # (C, 2)
        x_smooth = x_filt_t + np.einsum("cij,cj->ci", Cgain, diff_x)

        diff_P = P_next_smooth - P_pred
        P_smooth = P_filt_t + Cgain @ diff_P @ np.transpose(Cgain, (0, 2, 1))

        smoothed_pos[t] = x_smooth[:, 0]
        smoothed_vel[t] = x_smooth[:, 1]
        smoothed_cov[t] = P_smooth

        x_next_smooth = x_smooth
        P_next_smooth = P_smooth

    return KalmanRTSResult(
        filtered_pos=filtered_pos,
        filtered_vel=filtered_vel,
        smoothed_pos=smoothed_pos,
        smoothed_vel=smoothed_vel,
        filtered_cov=filtered_cov,
        smoothed_cov=smoothed_cov,
    )
