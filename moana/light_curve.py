"""
Code for working with David Bennett's light curve format.
"""
from __future__ import annotations

import itertools

try:
    from enum import StrEnum
except ImportError:
    from backports.strenum import StrEnum

import re
import warnings

import numpy as np
import pandas as pd
from io import StringIO
from enum import Enum
from typing import Optional, List, Dict
from pathlib import Path

from moana.dbc import Output

event_name = 'MB20208'


class ColumnName(StrEnum):
    TIME__MICROLENSING_HJD = 'time__microlensing_hjd'
    TIME__HJD = 'time__hjd'
    FLUX = 'flux'
    FLUX_ERROR = 'flux_error'
    MAGNITUDE = 'magnitude'
    MAGNITUDE_ERROR = 'magnitude_error'
    PHOTOMETRIC_MEASUREMENT = 'photometric_measurement'
    PHOTOMETRIC_MEASUREMENT_ERROR = 'photometric_measurement_error'
    FULL_WIDTH_HALF_MAX = 'full_width_half_max'


class FitModelColumnName(StrEnum):
    CHI_SQUARED = 'chi_squared'
    CUMULATIVE_CHI_SQUARED = 'cumulative_chi_squared'
    MAGNIFICATION = 'magnification'
    MAGNIFICATION_ERROR = 'magnification_error'
    MAGNIFICATION_RESIDUAL = 'magnification_residual'
    X_POSITION = 'x_position'
    Y_POSITION = 'y_position'


class NoResidualFoundError(ValueError):
    pass


class LightCurve:
    """
    A class for working with David Bennett's light curve format.
    """

    def __init__(self, instrument_suffix: str, data_frame: pd.DataFrame):
        self.instrument_suffix: str = instrument_suffix
        self.data_frame: pd.DataFrame = data_frame

    @staticmethod
    def save_light_curve_to_david_bennett_format_file(path, light_curve_data_frame):
        """
        Saves a light curve data frame to a file of the format expected by David Bennett's code.

        :param path: The path to the output file.
        :param light_curve_data_frame: The light curve data frame.
        """
        light_curve_data_frame.to_csv(path, header=False, index=False, sep=' ')

    @classmethod
    def from_path(cls, path: Path) -> LightCurve:
        instrument_suffix = path.suffix[1:]
        light_curve_data_frame = pd.read_csv(
            path, names=[ColumnName.TIME__MICROLENSING_HJD.value, ColumnName.PHOTOMETRIC_MEASUREMENT.value,
                         ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value],
            delim_whitespace=True, skipinitialspace=True, index_col=False
        )
        light_curve_data_frame = light_curve_data_frame.sort_values(ColumnName.TIME__MICROLENSING_HJD).reset_index(drop=True)
        light_curve = cls(instrument_suffix, light_curve_data_frame)
        light_curve.data_frame = light_curve_data_frame
        return light_curve

    def to_path(self, path: Path) -> None:
        columns_to_save = [ColumnName.TIME__MICROLENSING_HJD.value]
        if ColumnName.PHOTOMETRIC_MEASUREMENT.value in self.data_frame.columns:
            columns_to_save.extend(
                [ColumnName.PHOTOMETRIC_MEASUREMENT.value, ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value])
        elif ColumnName.FLUX.value in self.data_frame.columns:
            columns_to_save.extend([ColumnName.FLUX.value, ColumnName.FLUX_ERROR.value])
        elif ColumnName.MAGNITUDE.value in self.data_frame.columns:
            columns_to_save.extend([ColumnName.MAGNITUDE.value, ColumnName.MAGNITUDE_ERROR.value])
        else:
            raise ValueError('Light curve did not conform to a known type.')
        self.data_frame.to_csv(path, header=False, columns=columns_to_save, index=False, sep=' ')

    @classmethod
    def load_normalization_parameters_from_residual_file(cls, residual_path: Path) -> pd.Series:
        """
        Load the light curve magnification normalization parameters from a residual file.

        :param residual_path: The path to the residual file.
        :return: The normalization parameters.
        """
        with residual_path.open() as residual_file:
            residual_file_lines = residual_file.readlines()
        header_line = ''
        value_line = ''
        for line_index, line in enumerate(residual_file_lines):
            if re.search(r'^\s*t\s+', line):  # Hitting a line starting with ` t ` means there no more parameter lines.
                break
            line_with_no_newline = line.replace('\n', ' ')  # We want to put everything on just two lines.
            if line_index % 2 == 0:  # Every other line is a header line.
                header_line += line_with_no_newline
            else:  # Every other other line is a value line.
                value_line += line_with_no_newline
        parameter_series = cls.extract_normalization_parameters_from_single_line_strings(header_line, value_line)
        return parameter_series

    @classmethod
    def load_normalization_parameters_from_david_bennett_fit_file(cls, fit_path: Path) -> pd.Series:
        """
        Load the light curve magnification normalization parameters from a David Bennett fit file.

        :param fit_path: The path to the residual file.
        :return: The normalization parameters.
        """
        with fit_path.open() as fit_file:
            fit_file_lines = fit_file.readlines()
        header_line = ''
        value_line = ''
        for line_index, line in enumerate(fit_file_lines):
            line_with_no_newline = line.replace('\n', ' ')  # We want to put everything on just two lines.
            if line_index % 2 == 0:  # Every other line is a header line.
                if re.search(r'[A-Za-z]', line) is None:
                    break  # If we hit what should be a header line with no alpha, we've reached the light curve table.
                header_line += line_with_no_newline
            else:  # Every other other line is a value line.
                value_line += line_with_no_newline
        parameter_series = cls.extract_normalization_parameters_from_single_line_strings(header_line, value_line)
        return parameter_series

    @staticmethod
    def extract_normalization_parameters_from_single_line_strings(header_line: str, value_line: str) -> pd.Series:
        """
        Extracts David Bennett normalization parameters from a header line and value line. Not intended as a stand alone
        function, but was significant duplication between the functions that use it.

        :param header_line: A line containing the headers for the normalization values.
        :param value_line: A line containing the values of the normalizations.
        :return: A Pandas series containing the normalization values.
        """
        normalization_parameters_string = header_line + '\n' + value_line
        parameter_table_string_io = StringIO(normalization_parameters_string)
        parameter_data_frame = pd.read_csv(parameter_table_string_io, delim_whitespace=True, skipinitialspace=True)
        parameter_series = parameter_data_frame.iloc[0]  # There's only a single row. Convert to series.
        parameter_series = parameter_series[parameter_series != 0]  # Zero values are just fillers.
        parameter_series = parameter_series.filter(regex=r'^(A0|A2).*')  # Keep only light curve normalization values.
        return parameter_series

    @classmethod
    def dictionary_from_david_bennett_fit_file(cls, fit_path: Path) -> Dict[str, LightCurve]:
        """
        Extracts the model fit light curves from a David Bennett fit file. Extracts a separate fit for each light curve
        to take into account differing color bands.

        :param fit_path: The path to the fit file.
        :return: A dictionary of the light curves, one for each instrument, with the key being the instrument suffix.
        """
        normalization_parameters_series = cls.load_normalization_parameters_from_david_bennett_fit_file(fit_path)
        with fit_path.open() as fit_file:
            fit_file_lines = fit_file.readlines()
        for line_index in itertools.count():
            line = fit_file_lines.pop(0)
            if line_index % 2 == 0:  # Every other line is a header line.
                if re.search(r'[A-Za-z]', line) is None:
                    fit_file_lines.insert(0, line)
                    break  # If we hit what should be a header line with no alpha, we've reached the light curve table.
        fit_data_frame = pd.read_csv(StringIO(''.join(fit_file_lines)), delim_whitespace=True,
                                     skipinitialspace=True)
        instrument_suffixes = []
        for normalization_parameter_name in normalization_parameters_series.index:
            if normalization_parameter_name.startswith('A0'):
                instrument_suffixes.append(normalization_parameter_name[2:])
        column_names = []
        column_names.append(ColumnName.TIME__MICROLENSING_HJD)
        column_names.append(FitModelColumnName.MAGNIFICATION)
        for instrument_suffix in instrument_suffixes:
            instrument_flux_name = f'{instrument_suffix}_flux'
            column_names.append(instrument_flux_name)
        column_names.append(FitModelColumnName.Y_POSITION)
        column_names.append(FitModelColumnName.X_POSITION)
        fit_data_frame.columns = column_names
        for instrument_suffix in instrument_suffixes:
            fit_data_frame[f'{instrument_suffix}_magnification'] = (
                    (fit_data_frame[f'{instrument_suffix}_flux'] -
                     normalization_parameters_series[f'A2{instrument_suffix}']) /
                    normalization_parameters_series[f'A0{instrument_suffix}']
            )
        light_curve_dictionary: Dict[str, LightCurve] = {}
        for instrument_suffix in instrument_suffixes:
            light_curve_data_frame = pd.DataFrame({
                ColumnName.TIME__MICROLENSING_HJD: fit_data_frame[ColumnName.TIME__MICROLENSING_HJD],
                FitModelColumnName.MAGNIFICATION: fit_data_frame[f'{instrument_suffix}_magnification'],
                ColumnName.FLUX: fit_data_frame[f'{instrument_suffix}_flux']
            })
            light_curve = LightCurve(instrument_suffix, light_curve_data_frame)
            light_curve_dictionary[instrument_suffix] = light_curve
        return light_curve_dictionary

    @classmethod
    def from_path_with_residuals_from_run(cls, light_curve_path: Path, run_path: Optional[Path] = None) -> LightCurve:
        if run_path is None:
            run_path = light_curve_path.parent.joinpath('run_1')
        run = Output(run_path.name, str(run_path.parent))
        run.load()
        run_residual_data_frame = run.resid
        light_curve = cls.from_path(light_curve_path)
        instrument_suffix = light_curve_path.suffix[1:]
        light_curve_residual_data_frame = run_residual_data_frame[run_residual_data_frame['sfx'] == instrument_suffix]
        if light_curve_residual_data_frame.shape[0] == 0:
            raise NoResidualFoundError(f'No residual found for light curve {instrument_suffix} from {run_path}.')
        assert np.allclose(light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD.value].values,
                           light_curve_residual_data_frame['date'].values)
        light_curve.data_frame[FitModelColumnName.CHI_SQUARED.value] = light_curve_residual_data_frame['chi2'].values
        light_curve.data_frame[FitModelColumnName.MAGNIFICATION.value] = \
            light_curve_residual_data_frame['mgf_data'].values
        light_curve.data_frame[
            FitModelColumnName.MAGNIFICATION_ERROR.value] = light_curve_residual_data_frame['sig_mgf'].values
        light_curve.data_frame[
            FitModelColumnName.MAGNIFICATION_RESIDUAL.value] = light_curve_residual_data_frame['res_mgf'].values
        return light_curve

    def remove_data_points_by_chi_squared_limit(self, chi_squared_limit: float = 16) -> float:
        self.data_frame = self.data_frame[self.data_frame[FitModelColumnName.CHI_SQUARED.value] < chi_squared_limit]
        return self.data_frame[FitModelColumnName.CHI_SQUARED.value].mean()

    def remove_data_points_by_error_relative_to_maximum_minimum_range(self, threshold: float = 0.1):
        maximum_measurement = self.data_frame[ColumnName.PHOTOMETRIC_MEASUREMENT.value].max()
        minimum_measurement = self.data_frame[ColumnName.PHOTOMETRIC_MEASUREMENT.value].min()
        difference = maximum_measurement - minimum_measurement
        absolute_threshold = difference * threshold
        self.data_frame = self.data_frame[
            self.data_frame[ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value] < absolute_threshold]

    @classmethod
    def list_for_run_directory_with_residuals(cls, directory_path: Path) -> List[LightCurve]:
        light_curve_paths = directory_path.glob('lc*')
        light_curves = []
        for light_curve_path in light_curve_paths:
            try:
                light_curve = cls.from_path_with_residuals_from_run(light_curve_path)
            except NoResidualFoundError as error:
                warnings.warn(error.args[0] + '\nExcluding light curve from list.')
                continue
            light_curves.append(light_curve)
        return light_curves

    @classmethod
    def list_for_run_directory(cls, directory_path: Path, with_residuals: bool = False) -> List[LightCurve]:
        light_curve_paths = directory_path.glob('lc*')
        light_curves = []
        for light_curve_path in light_curve_paths:
            if with_residuals:
                light_curve = cls.from_path_with_residuals_from_run(light_curve_path)
            else:
                light_curve = cls.from_path(light_curve_path)
            light_curves.append(light_curve)
        return light_curves

    @classmethod
    def save_list_to_directory(cls, light_curves: List[LightCurve], directory: Path):
        for light_curve in light_curves:
            light_curve.to_path(directory.joinpath(f'lc{event_name}.{light_curve.instrument_suffix}'))


if __name__ == '__main__':
    LightCurve.dictionary_from_david_bennett_fit_file(
        Path('data/mb20208/runs/single_source_binary_lens_moa_and_kmti_close/fit.lc_run_1'))
