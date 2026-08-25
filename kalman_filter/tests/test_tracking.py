import os
import unittest

import numpy as np

from kalman_filter.kalman import kalman_rts_smooth
from kalman_filter.boundary import resample_polyline, fit_circle
from kalman_filter.shape_params import (
    extract_profile_params,
    reconstruct_profile_boundary,
    DEFAULT_PROFILE_R,
)
from kalman_filter.pipeline import track_boundaries

TEST_JSON = os.path.join(
    os.path.dirname(__file__), "..", "..", "tests", "arcjet_test_150_400.json"
)


class TestKalmanRTS(unittest.TestCase):
    def setUp(self):
        rng = np.random.default_rng(42)
        self.rng = rng
        T = 100
        t = np.arange(T)
        # constant-velocity ground truth: position = 2 + 0.5*t
        self.truth = 2.0 + 0.5 * t
        self.noise_std = 3.0
        self.z = self.truth + rng.normal(0, self.noise_std, T)

    def test_smoothed_beats_raw_noise(self):
        result = kalman_rts_smooth(self.z, process_var=0.01, measurement_var=self.noise_std**2)
        raw_rmse = np.sqrt(np.mean((self.z - self.truth) ** 2))
        smoothed_rmse = np.sqrt(np.mean((result.smoothed_pos[:, 0] - self.truth) ** 2))
        self.assertLess(smoothed_rmse, raw_rmse)

    def test_smoothed_beats_or_matches_filtered(self):
        result = kalman_rts_smooth(self.z, process_var=0.01, measurement_var=self.noise_std**2)
        filtered_rmse = np.sqrt(np.mean((result.filtered_pos[:, 0] - self.truth) ** 2))
        smoothed_rmse = np.sqrt(np.mean((result.smoothed_pos[:, 0] - self.truth) ** 2))
        # RTS smoothing uses the whole sequence (forward + backward), so it
        # is never worse than the forward-only filtered estimate.
        self.assertLessEqual(smoothed_rmse, filtered_rmse + 1e-9)

    def test_multichannel_matches_single_channel(self):
        z2 = np.stack([self.z, self.z], axis=1)
        result = kalman_rts_smooth(z2, process_var=0.01, measurement_var=self.noise_std**2)
        np.testing.assert_allclose(result.smoothed_pos[:, 0], result.smoothed_pos[:, 1])

    def test_handles_missing_measurements(self):
        z = self.z.copy()
        z[40:45] = np.nan
        result = kalman_rts_smooth(z, process_var=0.01, measurement_var=self.noise_std**2)
        self.assertTrue(np.all(np.isfinite(result.filtered_pos)))
        self.assertTrue(np.all(np.isfinite(result.smoothed_pos)))
        # Estimate through the gap should still track the true linear trend.
        gap_rmse = np.sqrt(np.mean((result.smoothed_pos[40:45, 0] - self.truth[40:45]) ** 2))
        self.assertLess(gap_rmse, self.noise_std)


class TestBoundaryUtils(unittest.TestCase):
    def test_resample_polyline_length_and_endpoints(self):
        points = np.array([[0, 0], [1, 1], [2, 4], [3, 9]], dtype=float)
        out = resample_polyline(points, 25)
        self.assertEqual(out.shape, (25, 2))
        np.testing.assert_allclose(out[0], points[0])
        np.testing.assert_allclose(out[-1], points[-1])

    def test_fit_circle_recovers_known_circle(self):
        rng = np.random.default_rng(0)
        cx_true, cy_true, r_true = 50.0, -20.0, 100.0
        theta = np.linspace(0, 2 * np.pi, 200, endpoint=False)
        x = cx_true + r_true * np.cos(theta) + rng.normal(0, 0.2, theta.size)
        y = cy_true + r_true * np.sin(theta) + rng.normal(0, 0.2, theta.size)
        cx, cy, r = fit_circle(np.stack([x, y], axis=1))
        self.assertAlmostEqual(cx, cx_true, delta=1.0)
        self.assertAlmostEqual(cy, cy_true, delta=1.0)
        self.assertAlmostEqual(r, r_true, delta=1.0)

    def test_fit_circle_partial_arc_geometric_fit(self):
        # A partial arc is where the algebraic (Kasa) fit is known to be
        # biased; the geometric refinement should still recover it well.
        rng = np.random.default_rng(1)
        cx_true, cy_true, r_true = 0.0, 0.0, 300.0
        theta = np.linspace(-0.6, 0.6, 150)  # ~69 degree arc
        x = cx_true + r_true * np.cos(theta) + rng.normal(0, 0.3, theta.size)
        y = cy_true + r_true * np.sin(theta) + rng.normal(0, 0.3, theta.size)
        cx, cy, r = fit_circle(np.stack([x, y], axis=1))
        self.assertAlmostEqual(r, r_true, delta=5.0)


class TestShapeParams(unittest.TestCase):
    def test_profile_round_trip_at_anchors(self):
        # Build a synthetic parabolic "boundary": x = center - k*y_rel^2
        ycenter, radius = 300.0, 200.0
        y = np.linspace(ycenter - radius, ycenter + radius, 400)
        x = 100.0 - 30.0 * ((y - ycenter) / radius) ** 2
        edge = np.stack([x, y], axis=1).reshape(-1, 1, 2).astype(np.int32)

        params = extract_profile_params(edge, flow_direction="right", r_values=DEFAULT_PROFILE_R)
        boundary = reconstruct_profile_boundary(params, DEFAULT_PROFILE_R, "right", n_points=201)

        # The reconstructed curve should pass close to the true parabola.
        x_true = 100.0 - 30.0 * ((boundary[:, 1] - ycenter) / radius) ** 2
        self.assertLess(np.max(np.abs(boundary[:, 0] - x_true)), 3.0)


class TestTrackBoundariesIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.model = track_boundaries(
            TEST_JSON, key="MODEL", flow_direction="right", geometry="hemisphere"
        )
        cls.shock = track_boundaries(
            TEST_JSON, key="SHOCK", flow_direction="right", geometry="profile"
        )

    def test_shapes_and_finiteness(self):
        for results in (self.model, self.shock):
            T = len(results["frame_indices"])
            pw = results["pointwise"]
            sp = results["shape"]
            self.assertEqual(pw["smoothed"].shape[0], T)
            self.assertEqual(sp["smoothed_boundary"].shape[0], T)
            self.assertTrue(np.all(np.isfinite(pw["smoothed"])))
            self.assertTrue(np.all(np.isfinite(sp["smoothed_boundary"])))

    def test_pointwise_reduces_frame_to_frame_jitter(self):
        for results in (self.model, self.shock):
            pw = results["pointwise"]
            mid = pw["raw"].shape[1] // 2
            raw_jitter = np.std(np.diff(pw["raw"][:, mid, 0]))
            smoothed_jitter = np.std(np.diff(pw["smoothed"][:, mid, 0]))
            self.assertLess(smoothed_jitter, raw_jitter)

    def test_shape_parameter_reduces_frame_to_frame_jitter(self):
        for results in (self.model, self.shock):
            sp = results["shape"]
            mid = sp["raw_boundary"].shape[1] // 2
            raw_jitter = np.std(np.diff(sp["raw_boundary"][:, mid, 0]))
            smoothed_jitter = np.std(np.diff(sp["smoothed_boundary"][:, mid, 0]))
            self.assertLess(smoothed_jitter, raw_jitter)


if __name__ == "__main__":
    unittest.main()
