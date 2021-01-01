"""
Code for working with David Bennett's light curve format.
"""
from __future__ import annotations

import re
import numpy as np
import pandas as pd
from io import StringIO
from enum import Enum
from typing import Optional, List
from pathlib import Path

from moana.dbc import Output


event_name = 'MB20208'


class ColumnName(Enum):
    TIME__MICROLENSING_HJD = 'time__microlensing_hjd'
    FLUX = 'flux'
    FLUX_ERROR = 'flux_error'
    MAGNITUDE = 'magnitude'
    MAGNITUDE_ERROR = 'magnitude_error'
    PHOTOMETRIC_MEASUREMENT = 'photometric_measurement'
    PHOTOMETRIC_MEASUREMENT_ERROR = 'photometric_measurement_error'
    FULL_WIDTH_HALF_MAX = 'full_width_half_max'


class FitModelColumnName(Enum):
    CHI_SQUARED = 'chi_squared'
    MAGNIFICATION = 'magnification'
    MAGNIFICATION_ERROR = 'magnification_error'
    MAGNIFICATION_RESIDUAL = 'magnification_residual'


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
        light_curve = cls(instrument_suffix, light_curve_data_frame)
        light_curve.data_frame = light_curve_data_frame
        return light_curve

    def to_path(self, path: Path) -> None:
        columns_to_save = [ColumnName.TIME__MICROLENSING_HJD.value]
        if ColumnName.PHOTOMETRIC_MEASUREMENT.value in self.data_frame.columns:
            columns_to_save.extend([ColumnName.PHOTOMETRIC_MEASUREMENT.value, ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value])
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
        parameter_table_string_io = StringIO(header_line + '\n' + value_line)
        parameter_data_frame = pd.read_csv(parameter_table_string_io, delim_whitespace=True, skipinitialspace=True)
        parameter_series = parameter_data_frame.iloc[0]  # There's only a single row. Convert to series.
        parameter_series = parameter_series[parameter_series != 0]  # Zero values are just fillers.
        parameter_series = parameter_series.filter(regex=r'^(A0|A2).*')  # Keep only light curve normalization values.
        return parameter_series

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
        assert np.allclose(light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD.value],
                           light_curve_residual_data_frame['date'])
        light_curve.data_frame[FitModelColumnName.CHI_SQUARED.value] = light_curve_residual_data_frame['chi2']
        light_curve.data_frame[FitModelColumnName.MAGNIFICATION.value] = light_curve_residual_data_frame['mgf_data']
        light_curve.data_frame[
            FitModelColumnName.MAGNIFICATION_ERROR.value] = light_curve_residual_data_frame['sig_mgf']
        light_curve.data_frame[
            FitModelColumnName.MAGNIFICATION_RESIDUAL.value] = light_curve_residual_data_frame['res_mgf']
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
            light_curve = cls.from_path_with_residuals_from_run(light_curve_path)
            light_curves.append(light_curve)
        return light_curves

    @classmethod
    def save_list_to_directory(cls, light_curves: List[LightCurve]):
        for light_curve in light_curves:
            light_curve.to_path(Path(f'lc{event_name}.{light_curve.instrument_suffix}'))
