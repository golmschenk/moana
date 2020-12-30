import numpy as np
import pandas as pd

from moana.david_bennett_fit.light_curve import LightCurve, ColumnName


class TestLightCurve:
    def test_can_remove_data_points_with_high_error_relative_to_maximum_minimum_range(self):
        light_curve = LightCurve()
        light_curve.data_frame = pd.DataFrame({
            ColumnName.PHOTOMETRIC_MEASUREMENT.value: [0, 0, 10],
            ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value: [0.2, 1.1, 0.1]
        })
        light_curve.remove_data_points_by_error_relative_to_maximum_minimum_range(threshold=0.1)
        assert np.array_equal(light_curve.data_frame[ColumnName.PHOTOMETRIC_MEASUREMENT.value],
                              [0, 10])
        assert np.array_equal(light_curve.data_frame[ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value],
                              [0.2, 0.1])
