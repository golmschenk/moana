import copy
import numpy as np
import pandas as pd
from bokeh.layouts import gridplot
from bokeh.models import ColumnDataSource, Box, DataTable, TableColumn, ScientificFormatter, LayoutDOM
from pandas.api.types import is_numeric_dtype
from bokeh.plotting import Figure

from moana.david_bennett_fit.lens_model_parameter import LensModelParameter
from moana.david_bennett_fit.names import LensModelParameterNameEnum, BinaryLensModelParameterNameEnum, \
    BinarySourceModelParameterNameEnum
from moana.david_bennett_fit.run import Run
from moana.light_curve import LightCurve, ColumnName, FitModelColumnName
from moana.dbc import Output
from moana.viewer.color_mapper import ColorMapper
from moana.viewer.light_curve_viewer import LightCurveViewer


class RunFitViewer:
    @staticmethod
    def extract_instrument_specific_light_curve_data_frame(moana_data_frame: pd.DataFrame, instrument_suffix: str
                                                           ) -> pd.DataFrame:
        mask = moana_data_frame['sfx'] == instrument_suffix
        microlensing_hjd = moana_data_frame.loc[mask, 'date']
        magnification = moana_data_frame.loc[mask, 'mgf_data']
        magnification_error = moana_data_frame.loc[mask, 'sig_mgf']
        magnification_residual = moana_data_frame.loc[mask, 'res_mgf']
        light_curve_data_frame = pd.DataFrame({ColumnName.TIME__MICROLENSING_HJD.value: microlensing_hjd,
                                               'magnification': magnification,
                                               'magnification_error': magnification_error,
                                               'magnification_residual': magnification_residual})
        return light_curve_data_frame

    def add_instrument_data_points_of_run_to_light_curve_and_residual_figures(self, run: Run,
                                                                              light_curve_figure: Figure,
                                                                              residual_figure: Figure):
        self.add_all_instruments_data_points_of_run_to_figure(run, light_curve_figure)
        self.add_all_instruments_data_points_of_run_to_figure(run, residual_figure,
                                                              y_column_name='magnification_residual')

    def add_all_instruments_data_points_of_run_to_figure(self, run: Run, figure: Figure,
                                                         y_column_name: str = 'magnification'):
        instrument_suffixes = sorted(run.dbc_output.resid['sfx'].unique())
        for instrument_suffix in instrument_suffixes:
            color_mapper = ColorMapper()
            instrument_color = color_mapper.get_instrument_color(instrument_suffix)
            instrument_data_frame = self.extract_instrument_specific_light_curve_data_frame(run.dbc_output.resid,
                                                                                            instrument_suffix)
            LightCurveViewer.add_light_curve_points_with_errors_to_figure(
                figure, instrument_data_frame, instrument_suffix, instrument_color, y_column_name)

    def add_fit_of_run_to_light_curve_and_residual_figures(self, run: Run, light_curve_figure: Figure,
                                                           residual_figure: Figure):
        color_mapper = ColorMapper()
        fit_color = color_mapper.get_fit_color(str(run.path))
        fit_times = run.dbc_output.fitlc['date']
        if run.lens_model_parameter_name_enum == BinarySourceModelParameterNameEnum:
            fit_model_light_curve_dictionary = LightCurve.dictionary_from_david_bennett_fit_file(
                run.path.joinpath(f'fit.lc_{run.david_bennett_run_name}'))
            for instrument_suffix, fit_model_light_curve in fit_model_light_curve_dictionary.items():
                instrument_color = color_mapper.get_instrument_color(instrument_suffix)
                light_curve_figure.line(source=fit_model_light_curve.data_frame, x=ColumnName.TIME__MICROLENSING_HJD,
                                        y=FitModelColumnName.MAGNIFICATION, line_color=instrument_color, line_width=1,
                                        legend_label=f'{instrument_suffix} band fit')
        else:
            fit_magnifications = run.dbc_output.fitlc['mgf']
            fit_data_frame = pd.DataFrame({ColumnName.TIME__MICROLENSING_HJD.value: fit_times,
                                           'magnification': fit_magnifications})
            fit_data_source = ColumnDataSource(fit_data_frame)
            light_curve_figure.line(source=fit_data_source, x=ColumnName.TIME__MICROLENSING_HJD.value,
                                    legend_label='Fit', y='magnification', line_color=fit_color, line_width=2)
        residual_baseline_times = [fit_times.min(), fit_times.max()]
        residual_baseline_values = [0, 0]
        residual_guide_data_frame = pd.DataFrame({ColumnName.TIME__MICROLENSING_HJD.value: residual_baseline_times,
                                                  'residual': residual_baseline_values})
        residual_guide_data_source = ColumnDataSource(residual_guide_data_frame)
        residual_figure.line(source=residual_guide_data_source, x=ColumnName.TIME__MICROLENSING_HJD.value, y='residual',
                             line_color=fit_color, line_width=2, legend_label=run.display_name)

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

    def create_light_curve_with_residuals_view(self, run: Run) -> LayoutDOM:
        light_curve_figure = Figure(title=run.display_name)
        residual_figure = Figure(x_range=light_curve_figure.x_range)
        combination_grid_plot = gridplot([[light_curve_figure], [residual_figure]])
        light_curve_figure.sizing_mode = 'stretch_width'
        light_curve_figure.height = 500
        residual_figure.sizing_mode = 'stretch_width'
        residual_figure.height = 170
        combination_grid_plot.sizing_mode = 'stretch_width'
        self.add_instrument_data_points_of_run_to_light_curve_and_residual_figures(run, light_curve_figure,
                                                                                   residual_figure)
        self.add_all_instruments_data_points_of_run_to_figure(run, residual_figure,
                                                              y_column_name='magnification_residual')
        self.add_fit_of_run_to_light_curve_and_residual_figures(run, light_curve_figure, residual_figure)
        light_curve_figure.legend.click_policy = "hide"
        residual_figure.legend.visible = False
        return combination_grid_plot

    def create_comparison_view(self, run0: Run, run1: Run) -> LayoutDOM:
        comparison_view_components = self.create_comparison_view_components()
        light_curve_figure, residual_figure0, residual_figure1, combination_grid_plot = comparison_view_components
        scale, shift = self.calculate_mean_relative_instrument_scale_and_shift(run0, run1)
        run1 = self.reverse_scale_and_shift_run(run1, scale, shift)
        self.add_instrument_data_points_of_run_to_light_curve_and_residual_figures(run0, light_curve_figure,
                                                                                   residual_figure0)
        self.add_all_instruments_data_points_of_run_to_figure(run1, residual_figure1,
                                                              y_column_name='magnification_residual')
        self.add_fit_of_run_to_light_curve_and_residual_figures(run1, light_curve_figure, residual_figure1)
        self.add_fit_of_run_to_light_curve_and_residual_figures(run0, light_curve_figure, residual_figure0)
        light_curve_figure.legend.click_policy = "hide"
        residual_figure0.legend.visible = False
        residual_figure1.legend.visible = False
        return combination_grid_plot

    def create_run_parameter_comparison_table(
            self, run0: Run, run1: Run,) -> DataTable:
        run0_parameters = LensModelParameter.dictionary_from_david_bennett_input_file(
            run0.output_input_file_path, lens_parameter_name_enum=run0.lens_model_parameter_name_enum)
        run1_parameters = LensModelParameter.dictionary_from_david_bennett_input_file(
            run1.output_input_file_path, lens_parameter_name_enum=run1.lens_model_parameter_name_enum)
        comparison_dictionary = {'run': [run0.display_name, run1.display_name, 'difference'],
                                 'chisq': [run0.dbc_output.param['chisq'], run1.dbc_output.param['chisq'],
                                           run0.dbc_output.param['chisq'] - run1.dbc_output.param['chisq']]}
        for key in list(dict.fromkeys(list(run0_parameters.keys()) + list(run1_parameters.keys()))):
            try:
                run0_value = run0_parameters[key].value
            except KeyError:
                run0_value = np.nan
            try:
                run1_value = run1_parameters[key].value
            except KeyError:
                run1_value = np.nan
            comparison_dictionary[key] = [run0_value, run1_value, run0_value - run1_value]
        comparison_data_frame = pd.DataFrame(comparison_dictionary)
        table_columns = []
        for column_name in comparison_data_frame.columns:
            if is_numeric_dtype(comparison_data_frame[column_name].dtype):
                formatter = ScientificFormatter(precision=5)
                table_columns.append(TableColumn(field=column_name, title=column_name, formatter=formatter))
            else:
                table_columns.append(TableColumn(field=column_name, title=column_name))
        comparison_data_table = DataTable(columns=table_columns, source=ColumnDataSource(comparison_data_frame),
                                          index_position=None)
        comparison_data_table.sizing_mode = 'stretch_width'
        comparison_data_table.height = 120
        return comparison_data_table

    def calculate_mean_relative_instrument_scale_and_shift(self, run0: Run, run1: Run) -> (float, float):
        residual_path0 = run0.residual_file_path
        residual_path1 = run1.residual_file_path
        parameter_series0 = LightCurve.load_normalization_parameters_from_residual_file(residual_path0)
        parameter_series1 = LightCurve.load_normalization_parameters_from_residual_file(residual_path1)
        parameter_data_frame = pd.DataFrame([parameter_series0, parameter_series1]).reset_index(drop=True)
        parameter_data_frame = parameter_data_frame.dropna(axis=1)
        scale_parameter_data_frame = parameter_data_frame.filter(regex=r'^A0.*')
        scale_parameter_data_frame.columns = scale_parameter_data_frame.columns.str.replace('^A0', '', regex=True)
        shift_parameter_data_frame = parameter_data_frame.filter(regex=r'^A2.*')
        shift_parameter_data_frame.columns = shift_parameter_data_frame.columns.str.replace('^A2', '', regex=True)
        relative_scale_series = scale_parameter_data_frame.iloc[0] / scale_parameter_data_frame.iloc[1]
        relative_shift_series = ((shift_parameter_data_frame.iloc[0] - shift_parameter_data_frame.iloc[1]) /
                                 scale_parameter_data_frame.iloc[1])
        instrument_data_count_series = run0.dbc_output.resid['sfx'].value_counts()
        instrument_data_count_series = instrument_data_count_series.filter(relative_scale_series.index)
        for suffix in relative_scale_series.keys():
            if suffix not in instrument_data_count_series.keys():
                instrument_data_count_series[suffix] = 0
        relative_scale = np.average(relative_scale_series.values, weights=instrument_data_count_series.values)
        relative_shift = np.average(relative_shift_series.values, weights=instrument_data_count_series.values)
        return relative_scale, relative_shift

    def calculate_mean_relative_instrument_magnification_scale_and_shift(
            self, run0: Run, run1: Run) -> (float, float):
        assert np.allclose(run0.dbc_output.resid['date'].values, run1.dbc_output.resid['date'].values)
        scale, shift = np.polyfit(run0.dbc_output.resid['mgf_model'].values,
                                  run1.dbc_output.resid['mgf_model'].values,
                                  1)
        return scale, shift

    def reverse_scale_and_shift_run(self, run: Run, scale: float, shift: float) -> Run:
        run = copy.deepcopy(run)
        output = run.dbc_output
        output.fitlc['mgf'] = (output.fitlc['mgf'] - shift) / scale
        output.resid['mgf_data'] = (output.resid['mgf_data'] - shift) / scale
        output.resid['res_mgf'] = output.resid['res_mgf'] / scale
        output.resid['sig_mgf'] = output.resid['sig_mgf'] / scale
        return run
