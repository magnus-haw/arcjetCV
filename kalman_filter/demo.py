"""Runnable demonstration of point-wise and shape-parameter Kalman/RTS
boundary tracking, applied to the sample (MODEL) and shock (SHOCK)
boundaries from the arcjetCV test video's bundled segmentation output.

Usage:
    python -m kalman_filter.demo
"""

import os

import matplotlib

matplotlib.use("Agg")

import numpy as np

from kalman_filter.pipeline import track_boundaries
from kalman_filter.visualize import plot_model_shock_comparison, animate_model_shock_boundaries
from kalman_filter.video_utils import load_video_frames

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.abspath(os.path.join(HERE, ".."))
DEFAULT_JSON = os.path.join(REPO_ROOT, "tests", "arcjet_test_150_400.json")
DEFAULT_VIDEO = os.path.join(REPO_ROOT, "tests", "arcjet_test.mp4")
DEFAULT_OUTPUT_DIR = os.path.join(HERE, "example_output")


def _jitter(x):
    """Std of frame-to-frame differences: a simple jitter metric used to
    quantify the "reduces local frame-to-frame fluctuations" claim."""
    return float(np.nanstd(np.diff(x)))


def main(
    json_path=DEFAULT_JSON,
    flow_direction="right",
    output_dir=DEFAULT_OUTPUT_DIR,
    video_path=DEFAULT_VIDEO,
):
    os.makedirs(output_dir, exist_ok=True)

    model_results = track_boundaries(
        json_path, key="MODEL", flow_direction=flow_direction, geometry="hemisphere"
    )
    shock_results = track_boundaries(
        json_path, key="SHOCK", flow_direction=flow_direction, geometry="profile"
    )
    frame_indices = model_results["frame_indices"]

    save_path = os.path.join(output_dir, "kalman_comparison.png")
    plot_model_shock_comparison(
        model_results, shock_results, frame_indices, save_path=save_path
    )

    video_frames = None
    if video_path and os.path.exists(video_path):
        video_frames = load_video_frames(video_path, frame_indices)
    else:
        print(f"Video not found ({video_path}) -- animating without footage.")

    gif_path = os.path.join(output_dir, "kalman_comparison.gif")
    animate_model_shock_boundaries(
        model_results,
        shock_results,
        frame_indices,
        save_path=gif_path,
        video_frames=video_frames,
    )

    for key, results in [("MODEL", model_results), ("SHOCK", shock_results)]:
        pw = results["pointwise"]
        sp = results["shape"]
        mid = pw["raw"].shape[1] // 2
        raw_x = pw["raw"][:, mid, 0]
        pw_x = pw["smoothed"][:, mid, 0]
        sp_x = sp["smoothed_boundary"][:, mid, 0]
        print(
            f"{key}: stagnation-point frame-to-frame jitter (std of diffs, px) -- "
            f"raw={_jitter(raw_x):.3f}  "
            f"point-wise={_jitter(pw_x):.3f}  "
            f"shape-parameter={_jitter(sp_x):.3f}"
        )

    print(f"Saved comparison figure to {save_path}")
    print(f"Saved comparison animation to {gif_path}")
    return model_results, shock_results


if __name__ == "__main__":
    main()
