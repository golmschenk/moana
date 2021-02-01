"""
Code to representing a microlensing parameter.
"""
from __future__ import annotations

import re
import numpy as np
import pandas as pd
from enum import Enum
from io import StringIO
from pathlib import Path
from typing import Union, Dict
from tabulate import tabulate
from file_read_backwards import FileReadBackwards


# noinspection SpellCheckingInspection
from moana.light_curve import FitModelColumnName


class LensModelParameterName(Enum):
    # TODO: These need better names
    INVERSE_EINSTEIN_CROSSING_TIME = '1/t_E'
    MINIMUM_APPROACH_TIME = 't0'
    MINIMUM_APPROACH_DISTANCE = 'umin'
    SECONDARY_SEPARATION = 'sep'
    SECONDARY_THETA = 'theta'
    SECONDARY_EPSILON = 'eps1'
    INVERSE_T_BIN = '1/Tbin'
    V_SEPARATION = 'v_sep'
    T_STAR = 'Tstar'
    T_FIX = 't_fix'
    PI_ER = 'piEr'
    PI_ETH = 'pieth'


class LensModelParameter:
    def __init__(self, value: float, temperature: float = 0, minimum_limit: Union[float, None] = None,
                 maximum_limit: Union[float, None] = None):
        if minimum_limit is None or maximum_limit is None:
            assert minimum_limit is None and maximum_limit is None
        self.value: float = value
        self.temperature: float = temperature
        self.minimum_limit: Union[float, None] = minimum_limit
        self.maximum_limit: Union[float, None] = maximum_limit

    @classmethod
    def dictionary_from_david_bennett_input_file(cls, input_file_path: Path) -> Dict[str, LensModelParameter]:
        """
        Loads the lens model parameters from a David Bennett input file.

        :param input_file_path: The path to the input file.
        :return: A dictionary of the lens parameters.
        """
        with input_file_path.open() as input_file:
            input_file_lines = input_file.readlines()
        lens_model_parameter_lines = []
        input_file_lines.pop(0)  # First line of the David Bennett input file format is a comment.
        for input_file_line in input_file_lines:
            match = re.match(r'[^\S\r\n]*\d', input_file_line)  # Match non-newline white-space followed by number.
            if match is None:
                break
            lens_model_parameter_lines.append(input_file_line)
        lens_model_parameter_content_string = ''.join(lens_model_parameter_lines)
        lens_model_parameter_string_io = StringIO(lens_model_parameter_content_string)
        lens_model_parameter_data_frame = pd.read_csv(
            lens_model_parameter_string_io, header=None,
            names=['index', 'name', 'value', 'temperature', 'minimum_limit', 'maximum_limit'],
            index_col='index', delim_whitespace=True, skipinitialspace=True, quotechar="'")
        lens_model_parameter_dictionary = {}
        allowed_names = [name.value for name in LensModelParameterName]
        for index, row in lens_model_parameter_data_frame.iterrows():
            assert row['name'] in allowed_names
            row_dictionary = row.dropna().to_dict()
            row_dictionary.pop('name')  # Remove the name entry from the dictionary to be input.
            lens_model_parameter_dictionary[row['name']] = LensModelParameter(**row_dictionary)
        return lens_model_parameter_dictionary

    @classmethod
    def david_bennett_input_string_from_dictionary(cls, parameter_dictionary: Dict[str, LensModelParameter]) -> str:
        """
        Converts a dictionary of lens model parameters to the input format expected by David Bennett's code.
        To prevent mistakes, requires exactly the parameters expected by David Bennett's code, no more or less.

        :param parameter_dictionary: The dictionary of parameters to convert the format of.
        :return: The string of the parameters in David Bennett's format.
        """
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

    @classmethod
    def dictionary_from_lowest_chi_squared_from_mcmc_run_output(cls, mcmc_run_path: Path
                                                                ) -> Dict[str, LensModelParameter]:
        lens_model_parameter_names = [name.value for name in LensModelParameterName]
        column_names = [FitModelColumnName.CHI_SQUARED.value, *lens_model_parameter_names]
        mcmc_output_dataframe = pd.read_csv(mcmc_run_path.joinpath('mcmc_run_1.dat'), delim_whitespace=True,
                                            usecols=list(range(len(column_names))), skipinitialspace=True, header=None,
                                            index_col=None, names=column_names)
        minimum_chi_squared_lens_parameter_row = mcmc_output_dataframe.iloc[
            mcmc_output_dataframe[FitModelColumnName.CHI_SQUARED.value].argmin()]
        lens_model_parameter_dictionary = cls.dictionary_from_david_bennett_input_file(
            mcmc_run_path.joinpath('run_1.in'))
        for lens_model_parameter_name, lens_model_parameter in lens_model_parameter_dictionary.items():
            lens_model_parameter.value = minimum_chi_squared_lens_parameter_row[lens_model_parameter_name]
        return lens_model_parameter_dictionary

    @classmethod
    def dictionary_from_lowest_chi_squared_from_run_output(cls, run_path: Path
                                                           ) -> Dict[str, LensModelParameter]:
        column_names = [name.value for name in LensModelParameterName]
        with FileReadBackwards(run_path.joinpath('run_1.out')) as file_read_backwards:
            while True:
                line = file_read_backwards.readline()
                if line.strip().startswith('accepted due to chi2 improvement'):
                    _ = file_read_backwards.readline()  # Discard chi squared value line.
                    lens_parameter_line = file_read_backwards.readline()
                    break
        lens_parameter_line = lens_parameter_line.replace('FCN call with a =', '').strip()
        lens_parameter_string_io = StringIO(lens_parameter_line)
        lens_parameter_data_frame = pd.read_csv(lens_parameter_string_io, delim_whitespace=True,
                                            usecols=list(range(len(column_names))), skipinitialspace=True, header=None,
                                            index_col=None, names=column_names)
        lens_parameter_row = lens_parameter_data_frame.iloc[0]
        lens_model_parameter_dictionary = cls.dictionary_from_david_bennett_input_file(run_path.joinpath('run_1.in'))
        for lens_model_parameter_name, lens_model_parameter in lens_model_parameter_dictionary.items():
            lens_model_parameter.value = lens_parameter_row[lens_model_parameter_name]
        return lens_model_parameter_dictionary

