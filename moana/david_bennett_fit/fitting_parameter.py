from __future__ import annotations

import re
import pandas as pd
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Union, Dict


# noinspection SpellCheckingInspection
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
            parameter_line = re.sub(r'^\s*#\s*(day.*)', r'\g<1>', parameter_line)
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
        assert False  # TODO: Finish
        available_names = [name.value for name in LensModelParameterName]
        for key in parameter_dictionary.keys():
            assert key in available_names
        parameter_dictionary_list = []
        for index, name in enumerate(available_names):
            parameter_dictionary_list.append({'index': index + 1, 'name': f"'{name}'",
                                              'value': parameter_dictionary[name].value,
                                              'temperature': parameter_dictionary[name].temperature,
                                              'minimum_limit': parameter_dictionary[name].minimum_limit,
                                              'maximum_limit': parameter_dictionary[name].maximum_limit})
        parameter_data_frame = pd.DataFrame(parameter_dictionary_list)
        parameter_data_frame = parameter_data_frame.astype({'index': int, 'name': str, 'value': float,
                                                            'temperature': float, 'minimum_limit': float,
                                                            'maximum_limit': float})
        list_of_lists = parameter_data_frame.values.tolist()
        # noinspection PyTypeChecker
        list_of_lists = [[element for element in list_ if pd.notna(element)] for list_ in list_of_lists]
        input_string = tabulate(list_of_lists, tablefmt='plain', floatfmt='.10')
        return input_string
