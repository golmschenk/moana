"""
Code for working with David Bennett's light curve format.
"""
import re
from enum import Enum
import numpy as np
import pandas as pd
from io import StringIO
from pathlib import Path

from moana.dbc import Output


class ColumnName(Enum):
    TIME__MICROLENSING_HJD = 'time_microlensing_hjd'
    FLUX = 'flux'
    FLUX_ERROR = 'flux_error'
    MAGNITUDE = 'magnitude'
    MAGNITUDE_ERROR = 'magnitude_error'
    PHOTOMETRIC_MEASUREMENT = 'photometric_measurement'
    PHOTOMETRIC_MEASUREMENT_ERROR = 'photometric_measurement_error'
    FULL_WIDTH_HALF_MAX = 'full_width_half_max'


class LightCurve:
    """
    A class for working with David Bennett's light curve format.
    """
    @staticmethod
    def save_light_curve_to_david_bennett_format_file(path, light_curve_data_frame):
        """
        Saves a light curve data frame to a file of the format expected by David Bennett's code.

        :param path: The path to the output file.
        :param light_curve_data_frame: The light curve data frame.
        """
        light_curve_data_frame.to_csv(path, header=False, index=False, sep=' ')

    @classmethod
    def from_path(cls, path: Path) -> pd.DataFrame:
        light_curve_data_frame = pd.read_csv(
            path, names=[ColumnName.TIME__MICROLENSING_HJD.value, ColumnName.PHOTOMETRIC_MEASUREMENT.value,
                         ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value],
            delim_whitespace=True, skipinitialspace=True
        )
        return light_curve_data_frame

    @staticmethod
    def to_path(light_curve_data_frame: pd.DataFrame, path: Path) -> None:
        columns_to_save = [ColumnName.TIME__MICROLENSING_HJD.value]
        if ColumnName.PHOTOMETRIC_MEASUREMENT.value in light_curve_data_frame.columns:
            columns_to_save.extend([ColumnName.PHOTOMETRIC_MEASUREMENT.value, ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value])
        elif ColumnName.FLUX.value in light_curve_data_frame.columns:
            columns_to_save.extend([ColumnName.FLUX.value, ColumnName.FLUX_ERROR.value])
        elif ColumnName.MAGNITUDE.value in light_curve_data_frame.columns:
            columns_to_save.extend([ColumnName.MAGNITUDE.value, ColumnName.MAGNITUDE_ERROR.value])
        else:
            raise ValueError('Light curve did not conform to a known type.')
        light_curve_data_frame.to_csv(path, header=False, columns=columns_to_save, index=False, sep=' ')

    @staticmethod
    def load_normalization_parameters_from_residual_file(residual_path: Path
                                                         ) -> pd.Series:
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
    def from_path_with_residuals_from_run(cls, light_curve_path: Path, run_path: Path):
        run = Output(run_path.name, str(run_path.parent))
        run.load()
        run_residual_data_frame = run.resid
        light_curve_data_frame = cls.from_path(light_curve_path)
        instrument_suffix = light_curve_path.suffix[1:]
        light_curve_residual_data_frame = run_residual_data_frame[run_residual_data_frame['sfx'] == instrument_suffix]
        assert np.allclose(light_curve_data_frame[ColumnName.TIME__MICROLENSING_HJD.value],
                           light_curve_residual_data_frame['date'])
        light_curve_data_frame['fit_chi_squared'] = light_curve_residual_data_frame['chi2']
        return light_curve_data_frame

    @classmethod
    def remove_data_points_by_chi_squared_limit(cls, light_curve_path: Path, run_path: Path,
                                                updated_light_curve_path: Path, chi_squared_limit: float = 16) -> float:
        light_curve_data_frame = cls.from_path_with_residuals_from_run(light_curve_path, run_path)
        updated_light_curve_data_frame = light_curve_data_frame[
            light_curve_data_frame['fit_chi_squared'] < chi_squared_limit]
        cls.to_path(updated_light_curve_data_frame, updated_light_curve_path)
        return light_curve_data_frame['fit_chi_squared'].mean()

