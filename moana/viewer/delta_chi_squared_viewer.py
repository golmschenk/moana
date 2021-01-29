"""
Code for displaying the delta chi squared.
"""
import numpy as np
from pathlib import Path
from bokeh.plotting import Figure

from moana.light_curve import LightCurve, FitModelColumnName, ColumnName
from moana.viewer.color_mapper import ColorMapper


class ChiSquaredViewer:
    @classmethod
    def for_comparison_of_two_fit_models(cls, run_path0: Path, run_path1: Path) -> Figure:
        color_mapper = ColorMapper()
        figure = Figure(x_axis_label='Time (Offset HJD)', y_axis_label='Cumulative delta chi squared')
        light_curves0 = LightCurve.list_for_run_directory_with_residuals(run_path0.parent)
        light_curve_dictionary0 = {light_curve.instrument_suffix: light_curve for light_curve in light_curves0}
        light_curves1 = LightCurve.list_for_run_directory_with_residuals(run_path1.parent)
        light_curve_dictionary1 = {light_curve.instrument_suffix: light_curve for light_curve in light_curves1}
        for instrument_suffix in light_curve_dictionary0.keys():
            light_curve0 = light_curve_dictionary0[instrument_suffix]
            light_curve1 = light_curve_dictionary1[instrument_suffix]
            delta_chi_squared = (light_curve0.data_frame[FitModelColumnName.CHI_SQUARED.value] -
                                 light_curve1.data_frame[FitModelColumnName.CHI_SQUARED.value])
            cumulative_delta_chi_squared = np.cumsum(delta_chi_squared)
            instrument_color = color_mapper.get_instrument_color(instrument_suffix)
            figure.line(x=light_curve0.data_frame[ColumnName.TIME__MICROLENSING_HJD.value],
                        y=cumulative_delta_chi_squared, line_color=instrument_color, line_width=2,
                        legend_label=instrument_suffix)
        figure.legend.location = 'top_left'
        return figure
