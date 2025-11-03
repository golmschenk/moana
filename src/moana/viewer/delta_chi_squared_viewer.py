"""
Code for displaying the delta chi squared.
"""
from typing import List

import numpy as np
import pandas as pd
from bokeh.plotting import Figure

from moana.david_bennett_fit.run import Run
from moana.light_curve import LightCurve, FitModelColumnName, ColumnName
from moana.viewer.color_mapper import ColorMapper


class ChiSquaredViewer:
    @classmethod
    def for_comparison_of_two_fit_models_per_instrument(cls, run0: Run, run1: Run) -> Figure:
        color_mapper = ColorMapper()
        figure = Figure(x_axis_label='Time (Offset HJD)', y_axis_label='Cumulative delta chi squared')
        light_curves0 = LightCurve.list_for_run_directory_with_residuals(run0.path)
        light_curve_dictionary0 = {light_curve.instrument_suffix: light_curve for light_curve in light_curves0}
        light_curves1 = LightCurve.list_for_run_directory_with_residuals(run1.path)
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
            figure.circle(x=light_curve0.data_frame[ColumnName.TIME__MICROLENSING_HJD.value],
                          y=cumulative_delta_chi_squared, color=instrument_color, legend_label=instrument_suffix,
                          fill_alpha=0.5)
        figure.legend.location = 'top_left'
        figure.legend.click_policy = 'hide'
        return figure

    @staticmethod
    def create_single_light_curve_data_frame_for_light_curves(light_curves: List[LightCurve]) -> pd.DataFrame:
        combined_light_curve_data_frame = pd.concat([light_curve.data_frame.copy() for light_curve in light_curves])
        combined_light_curve_data_frame.sort_values(by=ColumnName.TIME__MICROLENSING_HJD.value, inplace=True)
        return combined_light_curve_data_frame


    @classmethod
    def for_comparison_of_two_fit_models_total_chi_squared_value_using_(cls, run0: Run, run1: Run) -> Figure:
        figure = Figure(x_axis_label='Time (Offset HJD)', y_axis_label='Cumulative delta chi squared')

        light_curves0 = LightCurve.list_for_run_directory_with_residuals(run0.path)
        run0_data_frame = pd.concat([light_curve.data_frame.copy() for light_curve in light_curves0])
        light_curves1 = LightCurve.list_for_run_directory_with_residuals(run1.path)
        run1_data_frame = pd.concat([light_curve.data_frame.copy() for light_curve in light_curves1])
        merged_data_frame = run0_data_frame.merge(
            run1_data_frame, how='outer', on=ColumnName.TIME__MICROLENSING_HJD.value, suffixes=('_run0', '_run1'))
        merged_data_frame.sort_values(by=ColumnName.TIME__MICROLENSING_HJD.value, inplace=True)
        cumulative_delta = 0
        for index, row in merged_data_frame.iterrows():
            if pd.isna(row[FitModelColumnName.CHI_SQUARED.value + '_run0']):
                new_delta = row[FitModelColumnName.CHI_SQUARED.value + '_run1']
            elif pd.isna(row[FitModelColumnName.CHI_SQUARED.value + '_run1']):
                new_delta = -row[FitModelColumnName.CHI_SQUARED.value + '_run0']
            else:
                new_delta = row[FitModelColumnName.CHI_SQUARED.value + '_run1'] - row[FitModelColumnName.CHI_SQUARED.value + '_run0']
            cumulative_delta += new_delta
            merged_data_frame.loc[index, 'cumulative_delta_chi_squared'] = cumulative_delta
        # TODO: Need to handle if the two values do not line up.
        figure.line(x=merged_data_frame[ColumnName.TIME__MICROLENSING_HJD.value],
                    y=merged_data_frame['cumulative_delta_chi_squared'], line_width=2)
        figure.circle(x=merged_data_frame[ColumnName.TIME__MICROLENSING_HJD.value],
                      y=merged_data_frame['cumulative_delta_chi_squared'], fill_alpha=0.5)
        figure.legend.location = 'top_left'
        figure.legend.click_policy = 'hide'
        return figure