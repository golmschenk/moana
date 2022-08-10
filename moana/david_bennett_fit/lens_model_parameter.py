"""
Code to representing a microlensing parameter.
"""
from __future__ import annotations

import math
import re
import pandas as pd
from io import StringIO
from pathlib import Path
from typing import Union, Dict, Optional, Type
from tabulate import tabulate
from file_read_backwards import FileReadBackwards

# noinspection SpellCheckingInspection
from moana.david_bennett_fit.names import BinaryLensModelParameterNameEnum, LensModelParameterNameEnum, NameElement


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
    def dictionary_from_david_bennett_input_file(
            cls, input_file_path: Path,
            lens_parameter_name_enum: Type[LensModelParameterNameEnum] = BinaryLensModelParameterNameEnum
    ) -> Dict[NameElement, LensModelParameter]:
        """
        Loads the lens model parameters from a David Bennett input file.

        :param input_file_path: The path to the input file.
        :param lens_parameter_name_enum: The lens parameter name enum to use for this input file.
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
        lens_model_parameter_dictionary = cls.dictionary_from_david_bennett_input_string(
            lens_model_parameter_content_string, lens_parameter_name_enum)
        return lens_model_parameter_dictionary

    @classmethod
    def dictionary_from_david_bennett_input_string(
            cls, lens_model_parameter_input_string: str,
            lens_parameter_name_enum: Type[LensModelParameterNameEnum] = BinaryLensModelParameterNameEnum):
        lens_model_parameter_string_io = StringIO(lens_model_parameter_input_string)
        lens_model_parameter_data_frame = pd.read_csv(
            lens_model_parameter_string_io, header=None,
            names=['index', 'name', 'value', 'temperature', 'minimum_limit', 'maximum_limit'],
            index_col='index', delim_whitespace=True, skipinitialspace=True, quotechar="'")
        lens_model_parameter_dictionary = {}
        for index, row in lens_model_parameter_data_frame.iterrows():
            david_bennett_name = row['name']
            project_name = lens_parameter_name_enum.element_from_david_bennett_name(david_bennett_name)
            row_dictionary = row.dropna().to_dict()
            row_dictionary.pop('name')  # Remove the name entry from the dictionary to be input.
            lens_model_parameter_dictionary[project_name] = LensModelParameter(**row_dictionary)
        return lens_model_parameter_dictionary

    @classmethod
    def reformat_parameters_in_david_bennett_input_file(
            cls, input_file_path: Path,
            lens_parameter_name_enum: Type[LensModelParameterNameEnum] = BinaryLensModelParameterNameEnum) -> None:
        formatted_input_file_lines = []
        with input_file_path.open() as input_file:
            input_file_lines = input_file.readlines()
        lens_model_parameter_lines = []
        after_parameters_lines = []
        # First line of the David Bennett input file format is a comment.
        formatted_input_file_lines.append(input_file_lines.pop(0))
        in_parameter_lines = True
        for input_file_line in input_file_lines:
            if in_parameter_lines:
                match = re.match(r'[^\S\r\n]*\d', input_file_line)  # Match non-newline white-space followed by number.
                if match is None:
                    in_parameter_lines = False
                    after_parameters_lines.append(input_file_line)
                lens_model_parameter_lines.append(input_file_line)
            else:
                after_parameters_lines.append(input_file_line)
        lens_model_parameter_content_string = ''.join(lens_model_parameter_lines)
        parameter_dictionary = cls.dictionary_from_david_bennett_input_string(
            lens_model_parameter_content_string, lens_parameter_name_enum)
        formatted_parameter_input_string = cls.david_bennett_input_string_from_dictionary(
            parameter_dictionary, lens_parameter_name_enum=lens_parameter_name_enum)
        formatted_parameter_input_string += '\n'  # Add line breaks between parameters to instructions
        formatted_input_file_lines.append(formatted_parameter_input_string)
        formatted_input_file_lines.extend(after_parameters_lines)
        with input_file_path.open('w') as input_file:
            input_file.writelines(formatted_input_file_lines)

    @classmethod
    def david_bennett_input_string_from_dictionary(
            cls, parameter_dictionary: Dict[str, LensModelParameter],
            lens_parameter_name_enum: Type[LensModelParameterNameEnum] = BinaryLensModelParameterNameEnum) -> str:
        """
        Converts a dictionary of lens model parameters to the input format expected by David Bennett's code.
        To prevent mistakes, requires exactly the parameters expected by David Bennett's code, no more or less.

        :param parameter_dictionary: The dictionary of parameters to convert the format of.
        :param lens_parameter_name_enum: The lens parameter name enum to use for this input file.
        :return: The string of the parameters in David Bennett's format.
        """
        available_names = lens_parameter_name_enum.as_list()
        for key in parameter_dictionary.keys():
            assert key in available_names
        parameter_dictionary_list = []
        for index, name in enumerate(available_names):
            parameter_dictionary_list.append({'index': index + 1, 'name': f"'{name.david_bennett_name}'",
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
    def dictionary_from_most_recent_chi_squared_reduced_accepted_from_run_output(
            cls, run_path: Path, lens_parameter_name_enum: Type[LensModelParameterNameEnum] = BinaryLensModelParameterNameEnum
    ) -> Dict[str, LensModelParameter]:
        column_names = lens_parameter_name_enum.as_list()
        with FileReadBackwards(run_path.joinpath('run_1.out')) as file_read_backwards:
            while True:
                line = file_read_backwards.readline()
                if line.strip().startswith('accepted due to chi2 improvement'):
                    _ = file_read_backwards.readline()  # Discard chi squared value line.
                    lens_parameter_line = ''
                    while 'FCN call with a =' not in lens_parameter_line:
                        lens_parameter_line = file_read_backwards.readline().strip() + ' ' + lens_parameter_line
                    break
        lens_parameter_line = lens_parameter_line.replace('FCN call with a =', '').strip()
        lens_parameter_string_io = StringIO(lens_parameter_line)
        lens_parameter_data_frame = pd.read_csv(lens_parameter_string_io, delim_whitespace=True,
                                                usecols=list(range(len(column_names))), skipinitialspace=True,
                                                header=None,
                                                index_col=None, names=column_names)
        lens_parameter_row = lens_parameter_data_frame.iloc[0]
        lens_model_parameter_dictionary = cls.dictionary_from_david_bennett_input_file(run_path.joinpath('run_1.in'))
        for lens_model_parameter_name, lens_model_parameter in lens_model_parameter_dictionary.items():
            lens_model_parameter.value = lens_parameter_row[lens_model_parameter_name]
        return lens_model_parameter_dictionary

    @classmethod
    def dictionary_from_lowest_chi_squared_from_run_output(
            cls, run_path: Path,
            lens_parameter_name_enum: Type[LensModelParameterNameEnum] = BinaryLensModelParameterNameEnum,
            output_file_name='run_1.out'
    ) -> Dict[str, LensModelParameter]:
        column_names = lens_parameter_name_enum.as_list()
        lowest_chi_squared = math.inf
        with FileReadBackwards(run_path.joinpath(output_file_name)) as file_read_backwards:
            while True:
                line = file_read_backwards.readline()
                if line == '':
                    break
                if line.strip().startswith('accepted due to chi2 improvement'):
                    chi_squared_line = file_read_backwards.readline()
                    chi_squared = float(chi_squared_line.replace('chi2 =', ''))
                    if chi_squared < lowest_chi_squared:
                        lowest_chi_squared = chi_squared
                        lens_parameter_line = ''
                        while 'FCN call with a =' not in lens_parameter_line:
                            lens_parameter_line = file_read_backwards.readline().strip() + ' ' + lens_parameter_line
        lens_parameter_line = lens_parameter_line.replace('FCN call with a =', '').strip()
        lens_parameter_string_io = StringIO(lens_parameter_line)
        lens_parameter_data_frame = pd.read_csv(lens_parameter_string_io, delim_whitespace=True,
                                                usecols=list(range(len(column_names))), skipinitialspace=True,
                                                header=None,
                                                index_col=None, names=column_names)
        lens_parameter_row = lens_parameter_data_frame.iloc[0]
        lens_model_parameter_dictionary = cls.dictionary_from_david_bennett_input_file(run_path.joinpath('run_1.in'))
        for lens_model_parameter_name, lens_model_parameter in lens_model_parameter_dictionary.items():
            lens_model_parameter.value = lens_parameter_row[lens_model_parameter_name]
        return lens_model_parameter_dictionary
