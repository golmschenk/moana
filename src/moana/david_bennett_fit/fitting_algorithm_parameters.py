from __future__ import annotations

import re
import pandas as pd
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Union, Dict


# noinspection SpellCheckingInspection
from tabulate import tabulate


class FittingAlgorithmParameterName(Enum):
    # TODO: These need better names
    DETAILED_TIME_STEP_START = 'daycausmin'
    DETAILED_TIME_STEP_END = 'daycausmax'
    DELT_CAUS = 'deltcaus'
    DEL_FINE = 'delfine'
    INTEGRATION_GRID_RADIAL_STEP_SIZE = 'gridUstar'
    H_CUT = 'hcut'
    I_END = 'iend'
    INTEGRATION_GRID_RADIAL_TO_ANGULAR_RATIO = 'grid_rat'


class FittingAlgorithmParameters:
    def __init__(self, detailed_time_step_start: float, detailed_time_step_end: float, delt_caus: float,
                 del_fine: float, integration_grid_radial_step_size: float, h_cut: float, i_end: int,
                 integration_grid_radial_to_angular_ratio: float):
        self.detailed_time_step_start: float = detailed_time_step_start
        self.detailed_time_step_end: float = detailed_time_step_end
        self.delt_caus: float = delt_caus
        self.del_fine: float = del_fine
        self.integration_grid_radial_step_size: float = integration_grid_radial_step_size
        self.h_cut: float = h_cut
        self.i_end: int = i_end
        self.integration_grid_radial_to_angular_ratio: float = integration_grid_radial_to_angular_ratio

    @classmethod
    def from_david_bennett_parameter_file_path(cls, parameter_file_path: Path) -> FittingAlgorithmParameters:
        """
        Loads the fitting algorithm parameters from a David Bennett parameter file.

        :param parameter_file_path: The path to the parameter file.
        :return: The fitting algorithm parameters.
        """
        with parameter_file_path.open() as parameter_file:
            parameter_file_lines = parameter_file.readlines()
        fitting_algorithm_parameter_lines = []
        while re.search(r'#\s+jclr', parameter_file_lines[0]) is None:  # If we haven't reached the second header...
            parameter_line = parameter_file_lines.pop(0)  # Get the next line.
            parameter_line = re.sub(r'^\s*#\s*(day.*)', r'\g<1>', parameter_line)  # Remove the `#` from the header.
            fitting_algorithm_parameter_lines.append(parameter_line)  # Add the line.
        parameters_content_string = ''.join(fitting_algorithm_parameter_lines)
        parameters_string_io = StringIO(parameters_content_string)
        parameters_data_frame = pd.read_csv(parameters_string_io, delim_whitespace=True, skipinitialspace=True,
                                            quotechar="'")
        parameters_dictionary = parameters_data_frame.iloc[0].to_dict()
        fitting_algorithm_parameters = cls.from_dictionary(parameters_dictionary)
        return fitting_algorithm_parameters

    @classmethod
    def from_dictionary(cls, dictionary: Dict[str, Union[int, float]]) -> FittingAlgorithmParameters:
        fitting_algorithm_parameters = FittingAlgorithmParameters(
            detailed_time_step_start=dictionary[FittingAlgorithmParameterName.DETAILED_TIME_STEP_START.value],
            detailed_time_step_end=dictionary[FittingAlgorithmParameterName.DETAILED_TIME_STEP_END.value],
            delt_caus=dictionary[FittingAlgorithmParameterName.DELT_CAUS.value],
            del_fine=dictionary[FittingAlgorithmParameterName.DEL_FINE.value],
            integration_grid_radial_step_size=dictionary[
                FittingAlgorithmParameterName.INTEGRATION_GRID_RADIAL_STEP_SIZE.value],
            h_cut=dictionary[FittingAlgorithmParameterName.H_CUT.value],
            i_end=int(dictionary[FittingAlgorithmParameterName.I_END.value]),
            integration_grid_radial_to_angular_ratio=dictionary[
                FittingAlgorithmParameterName.INTEGRATION_GRID_RADIAL_TO_ANGULAR_RATIO.value]
        )
        return fitting_algorithm_parameters

    def to_david_bennett_parameter_file_string(self) -> str:
        parameter_dictionary = {
            FittingAlgorithmParameterName.DETAILED_TIME_STEP_START.value: self.detailed_time_step_start,
            FittingAlgorithmParameterName.DETAILED_TIME_STEP_END.value: self.detailed_time_step_end,
            FittingAlgorithmParameterName.DELT_CAUS.value: self.delt_caus,
            FittingAlgorithmParameterName.DEL_FINE.value: self.del_fine,
            FittingAlgorithmParameterName.INTEGRATION_GRID_RADIAL_STEP_SIZE.value:
                self.integration_grid_radial_step_size,
            FittingAlgorithmParameterName.H_CUT.value: self.h_cut,
            FittingAlgorithmParameterName.I_END.value: self.i_end,
            FittingAlgorithmParameterName.INTEGRATION_GRID_RADIAL_TO_ANGULAR_RATIO.value:
                self.integration_grid_radial_to_angular_ratio
        }
        parameter_list_dictionary = {key: [value] for key, value in parameter_dictionary.items()}
        file_string = tabulate(parameter_list_dictionary, tablefmt='plain', floatfmt='.10',
                               headers=parameter_list_dictionary.keys(), showindex=False)
        file_string = '# ' + file_string
        file_string = file_string.replace('\n', '\n  ')
        return file_string
