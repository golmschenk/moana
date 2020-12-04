import copy
import itertools
import random
import re
from pathlib import Path
import numpy as np
import pandas as pd
from bokeh import palettes
from bokeh.colors import Color
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, Whisker, Row, Box, DataTable, TableColumn, ScientificFormatter
from pandas.api.types import is_numeric_dtype
from bokeh.plotting import Figure

from moana.david_bennett_fit.light_curve import LightCurveFileLiaison
from moana.dbc import Output


class LightCurveViewer:
    def __init__(self):
        self.fit_colors = [element for element in itertools.chain.from_iterable(
            itertools.zip_longest(palettes.Greys[5][:4], palettes.Reds[5][:4])) if element]
        self.fit_name_to_color_dictionary = {}
        unshuffled_instrument_colors = list(palettes.Category20[20])
        random.seed(3)
        self.instrument_colors = random.sample(unshuffled_instrument_colors, len(unshuffled_instrument_colors))
        self.instrument_to_color_dictionary = {}

    @staticmethod
    def add_light_curve_points_with_errors_to_figure(figure: Figure, light_curve_data_frame: pd.DataFrame, name: str,
                                                     color: Color, y_column_name='magnification'):
        light_curve_data_frame = light_curve_data_frame.copy()
        light_curve_data_frame['plus_error'] = light_curve_data_frame[y_column_name
                                               ] + light_curve_data_frame['magnification_error']
        light_curve_data_frame['minus_error'] = light_curve_data_frame[y_column_name
                                                ] - light_curve_data_frame['magnification_error']
        source = ColumnDataSource(light_curve_data_frame)
        line_alpha = 0.8
        fill_alpha = 0.2
        circle_renderer = figure.circle(source=source, x='microlensing_hjd', y=y_column_name, legend_label=name,
                                        color=color, line_alpha=line_alpha, fill_alpha=fill_alpha)
        whisker = Whisker(source=source, base='microlensing_hjd', upper='plus_error',
                          lower='minus_error', line_alpha=line_alpha,
                          line_color=circle_renderer.glyph.fill_color)
        whisker.upper_head.line_color = circle_renderer.glyph.fill_color
        whisker.upper_head.line_alpha = line_alpha
        whisker.lower_head.line_color = circle_renderer.glyph.fill_color
        whisker.lower_head.line_alpha = line_alpha
        figure.add_layout(whisker)

    @staticmethod
    def extract_instrument_specific_light_curve_data_frame(moana_data_frame: pd.DataFrame, instrument_suffix: str
                                                           ) -> pd.DataFrame:
        mask = moana_data_frame['sfx'] == instrument_suffix
        microlensing_hjd = moana_data_frame.loc[mask, 'date']
        magnification = moana_data_frame.loc[mask, 'mgf_data']
        magnification_error = moana_data_frame.loc[mask, 'sig_mgf']
        magnification_residual = moana_data_frame.loc[mask, 'res_mgf']
        light_curve_data_frame = pd.DataFrame({'microlensing_hjd': microlensing_hjd,
                                               'magnification': magnification,
                                               'magnification_error': magnification_error,
                                               'magnification_residual': magnification_residual})
        return light_curve_data_frame

    def add_instrument_data_points_of_run_to_light_curve_and_residual_figures(self, run: Output,
                                                                              light_curve_figure: Figure,
                                                                              residual_figure: Figure):
        self.add_instrument_data_points_of_run_to_figure(run, light_curve_figure)
        self.add_instrument_data_points_of_run_to_figure(run, residual_figure, y_column_name='magnification_residual')

    def add_instrument_data_points_of_run_to_figure(self, run: Output, figure: Figure,
                                                    y_column_name: str = 'magnification'):
        instrument_suffixes = sorted(run.resid['sfx'].unique())
        for instrument_suffix in instrument_suffixes:
            instrument_color = self.get_instrument_color(instrument_suffix)
            instrument_data_frame = self.extract_instrument_specific_light_curve_data_frame(run.resid,
                                                                                            instrument_suffix)
            self.add_light_curve_points_with_errors_to_figure(figure, instrument_data_frame, instrument_suffix,
                                                              instrument_color, y_column_name)

    def get_instrument_color(self, instrument_suffix: str) -> Color:
        if instrument_suffix not in self.instrument_to_color_dictionary:
            self.instrument_to_color_dictionary[instrument_suffix] = self.instrument_colors.pop(0)
        return self.instrument_to_color_dictionary[instrument_suffix]

    def add_fit_of_run_to_light_curve_and_residual_figures(self, run: Output, light_curve_figure: Figure,
                                                           residual_figure: Figure):
        run_name = run.run
        if re.match(r'run_\d+(\.in)?', run_name):
            run_name = Path(run.path).stem
        run_name = run_name[-20:]
        fit_color = self.get_fit_color(run_name)
        fit_times = run.fitlc['date']
        fit_magnifications = run.fitlc['mgf']
        fit_data_frame = pd.DataFrame({'microlensing_hjd': fit_times, 'magnification': fit_magnifications})
        fit_data_source = ColumnDataSource(fit_data_frame)
        light_curve_figure.line(source=fit_data_source, x='microlensing_hjd', y='magnification', legend_label=run_name,
                                line_color=fit_color, line_width=2)

        residual_baseline_times = [fit_times.min(), fit_times.max()]
        residual_baseline_values = [0, 0]
        residual_guide_data_frame = pd.DataFrame({'microlensing_hjd': residual_baseline_times,
                                                  'residual': residual_baseline_values})
        residual_guide_data_source = ColumnDataSource(residual_guide_data_frame)
        residual_figure.line(source=residual_guide_data_source, x='microlensing_hjd', y='residual',
                             line_color=fit_color, line_width=2, legend_label=run_name)

    def get_fit_color(self, fit_name: str) -> Color:
        if fit_name not in self.fit_name_to_color_dictionary:
            self.fit_name_to_color_dictionary[fit_name] = self.fit_colors.pop(0)
        return self.fit_name_to_color_dictionary[fit_name]

    def create_comparison_view_components(self):
        light_curve_figure = Figure()
        residual_figure0 = Figure(x_range=light_curve_figure.x_range)
        residual_figure1 = Figure(x_range=light_curve_figure.x_range, y_range=residual_figure0.y_range)
        combination_grid_plot = gridplot([[light_curve_figure], [residual_figure0], [residual_figure1]])
        light_curve_figure.sizing_mode = 'stretch_width'
        light_curve_figure.height = 500
        for residual_figure in [residual_figure0, residual_figure1]:
            residual_figure.sizing_mode = 'stretch_width'
            residual_figure.height = 170
        combination_grid_plot.sizing_mode = 'stretch_width'
        return light_curve_figure, residual_figure0, residual_figure1, combination_grid_plot

    def create_comparison_view(self, run0: Output, run1: Output) -> Box:
        comparison_view_components = self.create_comparison_view_components()
        light_curve_figure, residual_figure0, residual_figure1, combination_grid_plot = comparison_view_components
        scale, shift = self.calculate_mean_relative_instrument_scale_and_shift(run0, run1)
        run1 = self.reverse_scale_and_shift_run(run1, scale, shift)
        self.add_instrument_data_points_of_run_to_light_curve_and_residual_figures(run0, light_curve_figure,
                                                                                   residual_figure0)
        self.add_instrument_data_points_of_run_to_figure(run1, residual_figure1,
                                                         y_column_name='magnification_residual')
        self.add_fit_of_run_to_light_curve_and_residual_figures(run1, light_curve_figure, residual_figure1)
        self.add_fit_of_run_to_light_curve_and_residual_figures(run0, light_curve_figure, residual_figure0)
        residual_figure0.legend.visible = False
        residual_figure1.legend.visible = False
        return combination_grid_plot

    def create_run_parameter_comparison_table(self, run0: Output, run1: Output) -> DataTable:
        run0_parameters: pd.Series = run0.param
        run1_parameters: pd.Series = run1.param
        column_names_to_keep = ['chisq', 't_E', 't0', 'umin', 'sep', 'theta', 'eps1', 'eps2', 'Tstar']
        run0_parameters = run0_parameters.filter(column_names_to_keep)
        run1_parameters = run1_parameters.filter(column_names_to_keep)
        difference_between_parameters = run0_parameters - run1_parameters
        comparison_data_frame = pd.concat([pd.DataFrame(run0_parameters).transpose(),
                                           pd.DataFrame(run1_parameters).transpose(),
                                           pd.DataFrame(difference_between_parameters).transpose()])
        comparison_data_frame.insert(0, 'run', [run0.run, run1.run, 'difference'])
        table_columns = []
        for column_name in comparison_data_frame.columns:
            formatter = None
            if is_numeric_dtype(comparison_data_frame[column_name].dtype):
                formatter = ScientificFormatter(precision=5)
            table_columns.append(TableColumn(field=column_name, title=column_name, formatter=formatter))
        comparison_data_table = DataTable(columns=table_columns, source=ColumnDataSource(comparison_data_frame),
                                          index_position=None)
        comparison_data_table.sizing_mode = 'stretch_width'
        comparison_data_table.height = 100
        return comparison_data_table

    def calculate_mean_relative_instrument_scale_and_shift(self, run0: Output, run1: Output) -> (float, float):
        run_path0 = Path(run0.path)
        run_path1 = Path(run1.path)
        residual_path0 = run_path0.joinpath(f'resid.{run0.run}')
        residual_path1 = run_path1.joinpath(f'resid.{run1.run}')
        liaison = LightCurveFileLiaison()
        parameter_series0 = liaison.load_normalization_parameters_from_residual_file(residual_path0)
        parameter_series1 = liaison.load_normalization_parameters_from_residual_file(residual_path1)
        parameter_data_frame = pd.DataFrame([parameter_series0, parameter_series1]).reset_index(drop=True)
        parameter_data_frame = parameter_data_frame.dropna(axis=1)
        scale_parameter_data_frame = parameter_data_frame.filter(regex=r'^A0.*')
        scale_parameter_data_frame.columns = scale_parameter_data_frame.columns.str.replace('A0', '')
        shift_parameter_data_frame = parameter_data_frame.filter(regex=r'^A2.*')
        shift_parameter_data_frame.columns = shift_parameter_data_frame.columns.str.replace('A2', '')
        relative_scale_series = scale_parameter_data_frame.iloc[0] / scale_parameter_data_frame.iloc[1]
        relative_shift_series = ((shift_parameter_data_frame.iloc[0] - shift_parameter_data_frame.iloc[1]) /
                                 scale_parameter_data_frame.iloc[1])
        instrument_data_count_series = run0.resid['sfx'].value_counts()
        instrument_data_count_series = instrument_data_count_series.filter(relative_scale_series.index)
        relative_scale = np.average(relative_scale_series.values, weights=instrument_data_count_series.values)
        relative_shift = np.average(relative_shift_series.values, weights=instrument_data_count_series.values)
        return relative_scale, relative_shift

    def reverse_scale_and_shift_run(self, run: Output, scale: float, shift: float) -> Output:
        run = copy.deepcopy(run)
        run.fitlc['mgf'] = (run.fitlc['mgf'] - shift) / scale
        run.resid['mgf_data'] = (run.resid['mgf_data'] - shift) / scale
        run.resid['res_mgf'] = run.resid['res_mgf'] / scale
        run.resid['sig_mgf'] = run.resid['sig_mgf'] / scale
        return run
