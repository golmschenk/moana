"""
Code for working with David Bennett's light curve format.
"""
import re
import pandas as pd
from io import StringIO
from pathlib import Path


class LightCurveFileLiaison:
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

    def load_light_curve_magnification_normalization_parameters_from_residual_file(self, residual_path: Path
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
        parameter_series = parameter_series.filter(regex=r'(A0|A2).*')  # Keep only light curve normalization values.
        return parameter_series
