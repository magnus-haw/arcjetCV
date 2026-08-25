"""Comparison plots for point-wise vs. shape-parameter Kalman/RTS boundary
tracking, in the style of the arcjetCV filtering-extension figure: boundary
overlays at a single frame, plus a frame-to-frame metric trace showing the
jitter reduction from filtering/smoothing.
"""

import numpy as np


def _stagnation_x(boundary):
    """x-coordinate of the mid-index point of a resampled/reconstructed
    boundary, used as a simple frame-to-frame recession/jitter metric."""
    mid = boundary.shape[1] // 2
    return boundary[:, mid, 0]


def plot_kalman_comparison(results, frame_indices, key="MODEL", frame_to_show=None, save_path=None):
    """Plot raw/point-wise/shape-parameter boundaries at one frame, and the
    corresponding stagnation-point trace across all frames.

    :param results: output of
        :func:`kalman_filter.pipeline.track_boundaries`.
    :param frame_indices: list of frame INDEX values (same order as the
        arrays inside ``results``).
    :param key: label used in the figure title ("MODEL" or "SHOCK").
    :param frame_to_show: index (into the arrays, not the video frame
        number) of the frame to display in the boundary-overlay panel;
        defaults to the last frame with a valid raw boundary.
    :param save_path: if given, save the figure to this path.
    :returns: the matplotlib Figure.
    """
    import matplotlib.pyplot as plt

    pw = results["pointwise"]
    sp = results["shape"]

    valid = np.where(~np.isnan(pw["raw"][:, 0, 0]))[0]
    if frame_to_show is None:
        frame_to_show = valid[-1] if len(valid) else 0

    fig, axes = plt.subplots(1, 2, figsize=(11, 5))

    ax = axes[0]
    raw_b = pw["raw"][frame_to_show]
    pw_b = pw["smoothed"][frame_to_show]
    sp_b = sp["smoothed_boundary"][frame_to_show]
    ax.plot(raw_b[:, 0], raw_b[:, 1], "o", ms=3, color="0.6", label="raw (resampled)")
    ax.plot(pw_b[:, 0], pw_b[:, 1], "-", lw=2, label="point-wise Kalman+RTS")
    ax.plot(sp_b[:, 0], sp_b[:, 1], "--", lw=2, label="shape-parameter Kalman+RTS")
    ax.set_title(f"{key} boundary, frame {frame_indices[frame_to_show]}")
    ax.set_xlabel("x [px]")
    ax.set_ylabel("y [px]")
    ax.invert_yaxis()
    ax.set_aspect("equal", adjustable="datalim")
    ax.legend(fontsize=8)

    ax = axes[1]
    x_raw = _stagnation_x(pw["raw"])
    x_pw = _stagnation_x(pw["smoothed"])
    x_sp = _stagnation_x(sp["smoothed_boundary"])
    ax.plot(frame_indices, x_raw, "o", ms=3, color="0.6", label="raw")
    ax.plot(frame_indices, x_pw, "-", lw=2, label="point-wise Kalman+RTS")
    ax.plot(frame_indices, x_sp, "--", lw=2, label="shape-parameter Kalman+RTS")
    ax.set_title(f"{key} stagnation-point x-position vs. frame")
    ax.set_xlabel("frame index")
    ax.set_ylabel("x [px]")
    ax.legend(fontsize=8)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig


def animate_model_shock_boundaries(
    model_results, shock_results, frame_indices, save_path, fps=4, video_frames=None
):
    """Animate raw/point-wise/shape-parameter boundaries evolving over all
    frames, MODEL and SHOCK side by side, and save as a GIF.

    :param model_results: output of
        :func:`kalman_filter.pipeline.track_boundaries` for key="MODEL".
    :param shock_results: same, for key="SHOCK".
    :param frame_indices: list of frame INDEX values (same order as the
        arrays inside the results dicts).
    :param save_path: output .gif path.
    :param fps: playback speed, frames per second.
    :param video_frames: optional list (same length/order as
        ``frame_indices``) of source-video frames, in the same pixel
        coordinate system as the stored contours (see
        :func:`kalman_filter.video_utils.load_video_frames`). If given, an
        extra leftmost panel shows the actual footage with both boundaries
        overlaid, alongside the MODEL/SHOCK detail panels.
    :returns: save_path.
    """
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation, PillowWriter

    datasets = [("MODEL", model_results), ("SHOCK", shock_results)]
    colors = {"MODEL": "tab:green", "SHOCK": "magenta"}
    n_frames = len(frame_indices)
    has_video = video_frames is not None

    ncols = 3 if has_video else 2
    fig, axes = plt.subplots(1, ncols, figsize=(5 * ncols, 5.5))
    axes = np.atleast_1d(axes)
    detail_axes = axes[1:] if has_video else axes

    video_artists = None
    if has_video:
        vax = axes[0]
        first_frame = next((f for f in video_frames if f is not None), None)
        placeholder = np.zeros_like(first_frame) if first_frame is not None else np.zeros((10, 10, 3), dtype=np.uint8)
        im = vax.imshow(placeholder)
        vax.set_xlabel("x [px]")
        vax.set_ylabel("y [px]")
        video_lines = {}
        for key, _ in datasets:
            c = colors[key]
            (raw_s,) = vax.plot([], [], "o", ms=2, color="white", mec=c, mew=0.5)
            (pw_l,) = vax.plot([], [], "-", lw=1.5, color=c, label=f"{key} point-wise")
            (sp_l,) = vax.plot([], [], "--", lw=1.5, color=c, alpha=0.6, label=f"{key} shape-param")
            video_lines[key] = (raw_s, pw_l, sp_l)
        vax.legend(fontsize=6, loc="upper right")
        video_artists = (im, video_lines, vax)

    artists = []
    for ax, (key, results) in zip(detail_axes, datasets):
        pw = results["pointwise"]
        sp = results["shape"]

        all_x = np.concatenate([pw["raw"][:, :, 0].ravel(), pw["smoothed"][:, :, 0].ravel()])
        all_y = np.concatenate([pw["raw"][:, :, 1].ravel(), pw["smoothed"][:, :, 1].ravel()])
        all_x = all_x[np.isfinite(all_x)]
        all_y = all_y[np.isfinite(all_y)]
        pad = 10
        ax.set_xlim(all_x.min() - pad, all_x.max() + pad)
        ax.set_ylim(all_y.max() + pad, all_y.min() - pad)  # inverted (image coords)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel("x [px]")
        ax.set_ylabel("y [px]")

        raw_scatter, = ax.plot([], [], "o", ms=3, color="0.6", label="raw (resampled)")
        pw_line, = ax.plot([], [], "-", lw=2, color=colors[key], label="point-wise Kalman+RTS")
        sp_line, = ax.plot([], [], "--", lw=2, color=colors[key], alpha=0.6, label="shape-parameter Kalman+RTS")
        ax.legend(fontsize=7, loc="upper right")
        artists.append((key, pw, sp, raw_scatter, pw_line, sp_line, ax))

    fig.tight_layout()

    def update(i):
        updated = []
        for key, pw, sp, raw_scatter, pw_line, sp_line, ax in artists:
            raw_scatter.set_data(pw["raw"][i, :, 0], pw["raw"][i, :, 1])
            pw_line.set_data(pw["smoothed"][i, :, 0], pw["smoothed"][i, :, 1])
            sp_line.set_data(sp["smoothed_boundary"][i, :, 0], sp["smoothed_boundary"][i, :, 1])
            ax.set_title(f"{key}, frame {frame_indices[i]}")
            updated.extend([raw_scatter, pw_line, sp_line])

        if video_artists is not None:
            im, video_lines, vax = video_artists
            frame = video_frames[i]
            if frame is not None:
                im.set_data(frame)
            for key, results in datasets:
                pw = results["pointwise"]
                sp = results["shape"]
                raw_s, pw_l, sp_l = video_lines[key]
                raw_s.set_data(pw["raw"][i, :, 0], pw["raw"][i, :, 1])
                pw_l.set_data(pw["smoothed"][i, :, 0], pw["smoothed"][i, :, 1])
                sp_l.set_data(sp["smoothed_boundary"][i, :, 0], sp["smoothed_boundary"][i, :, 1])
                updated.extend([raw_s, pw_l, sp_l])
            vax.set_title(f"source video, frame {frame_indices[i]}")
            updated.append(im)

        return updated

    anim = FuncAnimation(fig, update, frames=n_frames, blit=False)
    anim.save(save_path, writer=PillowWriter(fps=fps))
    plt.close(fig)
    return save_path


def plot_model_shock_comparison(model_results, shock_results, frame_indices, save_path=None):
    """Two-row version of :func:`plot_kalman_comparison`: sample (MODEL) on
    top, shock on bottom, each with a boundary-overlay panel and a
    stagnation-point trace panel.

    :returns: the matplotlib Figure.
    """
    import matplotlib.pyplot as plt

    fig, axes = plt.subplots(2, 2, figsize=(11, 9))
    for row, (key, results) in enumerate([("MODEL", model_results), ("SHOCK", shock_results)]):
        pw = results["pointwise"]
        sp = results["shape"]

        valid = np.where(~np.isnan(pw["raw"][:, 0, 0]))[0]
        frame_to_show = valid[-1] if len(valid) else 0

        ax = axes[row, 0]
        raw_b = pw["raw"][frame_to_show]
        pw_b = pw["smoothed"][frame_to_show]
        sp_b = sp["smoothed_boundary"][frame_to_show]
        ax.plot(raw_b[:, 0], raw_b[:, 1], "o", ms=3, color="0.6", label="raw (resampled)")
        ax.plot(pw_b[:, 0], pw_b[:, 1], "-", lw=2, label="point-wise Kalman+RTS")
        ax.plot(sp_b[:, 0], sp_b[:, 1], "--", lw=2, label="shape-parameter Kalman+RTS")
        ax.set_title(f"{key} boundary, frame {frame_indices[frame_to_show]}")
        ax.set_xlabel("x [px]")
        ax.set_ylabel("y [px]")
        ax.invert_yaxis()
        ax.set_aspect("equal", adjustable="datalim")
        ax.legend(fontsize=8)

        ax = axes[row, 1]
        x_raw = _stagnation_x(pw["raw"])
        x_pw = _stagnation_x(pw["smoothed"])
        x_sp = _stagnation_x(sp["smoothed_boundary"])
        ax.plot(frame_indices, x_raw, "o", ms=3, color="0.6", label="raw")
        ax.plot(frame_indices, x_pw, "-", lw=2, label="point-wise Kalman+RTS")
        ax.plot(frame_indices, x_sp, "--", lw=2, label="shape-parameter Kalman+RTS")
        ax.set_title(f"{key} stagnation-point x-position vs. frame")
        ax.set_xlabel("frame index")
        ax.set_ylabel("x [px]")
        ax.legend(fontsize=8)

    fig.tight_layout()
    if save_path:
        fig.savefig(save_path, dpi=150)
    return fig
