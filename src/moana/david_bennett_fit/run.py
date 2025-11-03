"""
Code to represent an existing run.
"""
from __future__ import annotations

import re
import shutil
from io import StringIO

import pandas as pd
from pathlib import Path
from typing import Optional, List, Type, Dict

from file_read_backwards import FileReadBackwards

from moana.david_bennett_fit.lens_model_parameter import LensModelParameter
from moana.david_bennett_fit.names import BinaryLensModelParameterNameEnum, BinarySourceModelParameterNameEnum, \
    LensModelParameterNameEnum, NameEnum, NameElement
from moana.dbc import Output
from moana.light_curve import FitModelColumnName


class Run:
    """
    A class to represent an existing run.
    """
    def __init__(self, path: Path, david_bennett_run_name: str = 'run_1', output_input_file_name: str = 'run_2.in',
                 display_name: Optional[str] = None):
        self.path: Path = path
        self.david_bennett_run_name: str = david_bennett_run_name
        self.output_input_file_name: str = output_input_file_name
        self._display_name: Optional[str] = display_name
        self._dbc_output: Optional[Output] = None
        self._lens_model_parameter_name_enum: Optional[Type[LensModelParameterNameEnum]] = None

    @property
    def lens_model_parameter_name_enum(self) -> Type[LensModelParameterNameEnum]:
        if self._lens_model_parameter_name_enum is None:
            self._lens_model_parameter_name_enum = self.infer_lens_model_parameter_name_enum_from_input_file()
        return self._lens_model_parameter_name_enum

    @property
    def display_name(self) -> str:
        if self._display_name is not None:
            return self._display_name
        else:
            return self.path.name

    @display_name.setter
    def display_name(self, value: str):
        self._display_name = value

    def set_display_name_from_run_path_difference(self, other_run: Run) -> str:
        split_name0 = self.path.name.split('_')
        split_name1 = other_run.path.name.split('_')
        split_display_name = [part for part in split_name0 if part not in split_name1]
        display_name = '_'.join(split_display_name)
        return display_name

    @property
    def input_file_name(self) -> str:
        return self.david_bennett_run_name + '.in'

    @property
    def dbc_output(self) -> Output:
        if self._dbc_output is None:
            self._dbc_output = Output(run=self.david_bennett_run_name, path=str(self.path))
            self._dbc_output.load()
        return self._dbc_output

    @property
    def input_file_path(self) -> Path:
        return self.path.joinpath(self.input_file_name)

    @property
    def output_input_file_path(self) -> Path:
        return self.path.joinpath(self.output_input_file_name)

    @property
    def main_output_file_path(self) -> Path:
        return self.path.joinpath(self.david_bennett_run_name + '.out')

    @property
    def residual_file_path(self) -> Path:
        return self.path.joinpath(f'resid.{self.david_bennett_run_name}')

    @classmethod
    def make_short_display_names_from_unique_directory_name_components(cls, runs: List[Run]):
        if len(runs) != 2:
            raise NotImplementedError
        run0 = runs[0]
        run1 = runs[1]
        split_name0 = run0.path.name.split('_')
        split_name1 = run1.path.name.split('_')
        split_display_name0 = [part if part not in split_name1 else '...' for part in split_name0]
        split_display_name1 = [part if part not in split_name0 else '...' for part in split_name1]

        def remove_repeat_ellipsis(string_list: List[str]):
            string_list_without_repeat_ellipsis = []
            previous_part = ''
            for part in string_list:
                if not (part == '...' and previous_part == '...'):
                    string_list_without_repeat_ellipsis.append(part)
                previous_part = part
            return string_list_without_repeat_ellipsis

        shorter_split_name0 = remove_repeat_ellipsis(split_display_name0)
        shorter_split_name1 = remove_repeat_ellipsis(split_display_name1)
        run0.display_name = '_'.join(shorter_split_name0)
        run1.display_name = '_'.join(shorter_split_name1)

    @property
    def mcmc_output_file_path(self) -> Path:
        return self.path.joinpath('mcmc_run_1.dat')

    def infer_lens_model_parameter_name_enum_from_input_file(self) -> Type[LensModelParameterNameEnum]:
        try:
            LensModelParameter.dictionary_from_david_bennett_input_file(self.input_file_path)
            return BinaryLensModelParameterNameEnum
        except (AssertionError, KeyError):
            return BinarySourceModelParameterNameEnum

    def get_mcmc_output_file_state_count(self) -> int:
        state_repeat_column_index = -1
        mcmc_output_dataframe = pd.read_csv(self.mcmc_output_file_path, delim_whitespace=True, skipinitialspace=True,
                                            header=None, index_col=None)
        return mcmc_output_dataframe.iloc[:, state_repeat_column_index].sum()

    def get_mcmc_output_file_row_count(self) -> int:
        state_repeat_column_index = -1
        mcmc_output_dataframe = pd.read_csv(self.mcmc_output_file_path, delim_whitespace=True, skipinitialspace=True,
                                            header=None, index_col=None)
        return mcmc_output_dataframe.iloc[:, state_repeat_column_index].shape[0]

    def load_minimum_chi_squared_mcmc_output_state(self) -> pd.Series:
        mcmc_output_dataframe = self.load_mcmc_output_states()
        minimum_chi_squared_lens_parameter_row = mcmc_output_dataframe.iloc[
            mcmc_output_dataframe[FitModelColumnName.CHI_SQUARED.value].argmin()]
        return minimum_chi_squared_lens_parameter_row

    def remove_bad_chi_squared_rows_from_mcmc_file(self, multiple_of_best_threshold: float = 2.0):
        minimum_chi_squared_lens_parameter_row = self.load_minimum_chi_squared_mcmc_output_state()
        minimum_chi_squared = minimum_chi_squared_lens_parameter_row[0]
        replacement_path = self.mcmc_output_file_path.parent.joinpath(self.mcmc_output_file_path.name + '.tmp')
        with self.mcmc_output_file_path.open('r') as old_file, replacement_path.open('w') as new_file:
            for line in old_file.readlines():
                line_chi_squared = float(line.strip().split(' ')[0])
                if line_chi_squared < minimum_chi_squared * multiple_of_best_threshold:
                    new_file.write(line)
        shutil.copy(replacement_path, self.mcmc_output_file_path)
        replacement_path.unlink()

    def load_mcmc_output_states(self) -> pd.DataFrame:
        mcmc_output_dataframe = pd.read_csv(self.mcmc_output_file_path, delim_whitespace=True, skipinitialspace=True,
                                            header=None, index_col=None)
        lens_model_parameter_names = [name.david_bennett_name for name in self.lens_model_parameter_name_enum.as_list()]
        pre_flux_column_names = [FitModelColumnName.CHI_SQUARED.value, *lens_model_parameter_names]
        column_count = len(mcmc_output_dataframe.columns)
        flux_values_column_count = column_count - len(pre_flux_column_names) - 1  # Last column is MCMC state repeat.
        assert flux_values_column_count % 2 == 0  # There should be two columns for each flux band.
        flux_values_column_names = []
        for flux_column_index in range(flux_values_column_count // 2):
            flux_values_column_names.append(f'flux{flux_column_index}_scale')
            flux_values_column_names.append(f'flux{flux_column_index}_offset')
        mcmc_output_dataframe.columns = pre_flux_column_names + flux_values_column_names + ['state_repeat_count']
        return mcmc_output_dataframe

    def load_normalization_parameters_from_main_output_file(self) -> pd.DataFrame:
        normalization_parameter_lines = []
        with FileReadBackwards(self.main_output_file_path) as file_read_backwards:
            while True:
                line = file_read_backwards.readline()
                if line.strip().startswith('Normalization parameters'):
                    break
                if line.startswith('A0'):
                    normalization_parameter_lines.append(line)
        normalization_parameters = {}
        for normalization_parameter_line in normalization_parameter_lines:
            a0_pattern = r'\s*A0(\w+)\s*=\s*([+-]?\d+\.?\d*)\s*\+/-\s*(\d+\.?\d*)'
            a2_pattern = r'\s*A2\w+\s*=\s*([+-]?\d+\.?\d*)\s*\+/-\s*(\d+\.?\d*)'
            match = re.search(a0_pattern + a2_pattern, normalization_parameter_line)
            light_curve_normalization_parameters = {
                'a0': float(match.group(2)),
                'a0_error': float(match.group(3)),
                'a2': float(match.group(4)),
                'a2_error': float(match.group(5))
            }
            normalization_parameters[match.group(1)] = light_curve_normalization_parameters
        return pd.DataFrame(normalization_parameters)

    def delete_first_lines_from_mcmc_file(self, number_of_lines_to_delete: int):
        replacement_path = self.mcmc_output_file_path.parent.joinpath(self.mcmc_output_file_path.name + '.tmp')
        with self.mcmc_output_file_path.open('r') as old_file, replacement_path.open('w') as new_file:
            for line_index, line in enumerate(old_file.readlines()):
                if line_index < number_of_lines_to_delete:
                    continue
                else:
                    new_file.write(line)
        shutil.copy(replacement_path, self.mcmc_output_file_path)
        replacement_path.unlink()

    def lens_model_parameter_dictionary_from_lowest_chi_squared_from_mcmc_run_output(
            self) -> Dict[NameElement, LensModelParameter]:
        minimum_chi_squared_lens_parameter_row = self.load_minimum_chi_squared_mcmc_output_state()
        lens_model_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(
            self.input_file_path)
        for lens_model_parameter_name, lens_model_parameter in lens_model_parameter_dictionary.items():
            lens_model_parameter.value = minimum_chi_squared_lens_parameter_row[lens_model_parameter_name.david_bennett_name]
        return lens_model_parameter_dictionary

    def lens_model_parameter_dictionary_from_most_recent_mcmc_run_state(
            self, start: int) -> Dict[str, LensModelParameter]:
        states_data_frame = self.load_mcmc_output_states()
        last_state_row = states_data_frame.iloc[start]
        lens_model_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(
            self.input_file_path)
        for lens_model_parameter_name, lens_model_parameter in lens_model_parameter_dictionary.items():
            lens_model_parameter.value = last_state_row[lens_model_parameter_name]
        return lens_model_parameter_dictionary

    def extract_final_parameters_from_run_output_file(self) -> Dict[NameElement, LensModelParameter]:
        final_parameter_lines = []
        with FileReadBackwards(self.main_output_file_path) as file_read_backwards:
            # assert 'MINUIT TERMINATED BY MINUIT COMMAND: EXIT' in file_read_backwards.readline()
            while True:
                line = file_read_backwards.readline()
                if '=' in line:  # We've reached the normalization parameter rows.
                    break
                if 'Caustic crossings found at' in line:  # We've reached the caustic crossing lines.
                    while True:
                        pop_line = final_parameter_lines.pop(0)
                        if re.search(r'[A-Za-z]', pop_line) is not None:
                            final_parameter_lines.insert(0, pop_line)
                            break
                    break
                final_parameter_lines.insert(0, line)
        header_line = ''
        value_line = ''
        for line_index, line in enumerate(final_parameter_lines):
            line_with_no_newline = line.replace('\n', ' ')  # We want to put everything on just two lines.
            if line_index % 2 == 0:  # Every other line is a header line.
                if re.search(r'[A-Za-z]', line) is None:
                    break  # If we hit what should be a header line with no alpha, we've reached the light curve table.
                header_line += line_with_no_newline
            else:  # Every other other line is a value line.
                value_line += line_with_no_newline
        normalization_parameters_string = header_line + '\n' + value_line
        parameter_table_string_io = StringIO(normalization_parameters_string)
        parameter_data_frame = pd.read_csv(parameter_table_string_io, delim_whitespace=True, skipinitialspace=True)
        run_output_parameter_series = parameter_data_frame.iloc[0]  # There's only a single row. Convert to series.
        run_input_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(
            self.input_file_path, lens_parameter_name_enum=self.lens_model_parameter_name_enum)
        # Correct inconsistent inputs and outputs.
        if 'f2MRpowI.1' in run_output_parameter_series.index:
            run_output_parameter_series.rename(index={'f2MRpowI.1': 'f2KpowI'}, inplace=True)  # Typo by Dave.
        if 'T_Sbininv' in [name.david_bennett_name for name in self.lens_model_parameter_name_enum.as_list()]:
            run_output_parameter_series.rename(index={'1/T_Sbin': 'T_Sbininv'}, inplace=True)
        if ('1/t_E' in [name.david_bennett_name for name in self.lens_model_parameter_name_enum.as_list()]
                and 't_E' in run_output_parameter_series.index):
            run_output_parameter_series['1/t_E'] = 1 / run_output_parameter_series['t_E']
        if ('piEr' in [name.david_bennett_name for name in self.lens_model_parameter_name_enum.as_list()]
                and 'piEx' in run_output_parameter_series.index):
            run_output_parameter_series.rename(index={'piEx': 'piEr'}, inplace=True)
        if ('pieth' in [name.david_bennett_name for name in self.lens_model_parameter_name_enum.as_list()]
                and 'piEy' in run_output_parameter_series.index):
            run_output_parameter_series.rename(index={'piEy': 'pieth'}, inplace=True)
        if ('piEtheta' in run_output_parameter_series.index):
            run_output_parameter_series.rename(index={'piEtheta': 'pieth'}, inplace=True)
        column_names_to_keep = [name.david_bennett_name for name in self.lens_model_parameter_name_enum.as_list()]
        column_names_to_keep.insert(0, NameEnum.CHI_SQUARED_STATISTIC.david_bennett_name)
        run_output_parameter_series = run_output_parameter_series.filter(items=column_names_to_keep)
        assert len(run_input_parameter_dictionary) + 1 == run_output_parameter_series.shape[0]  # +1 for the chi^2.
        for key, value in run_output_parameter_series.iteritems():
            parameter_name = NameEnum.element_from_david_bennett_name(key)
            try:
                run_input_parameter_dictionary[parameter_name].value = value
            except KeyError:
                run_input_parameter_dictionary[parameter_name] = LensModelParameter(value)
        return run_input_parameter_dictionary

    def remove_results_files(self) -> None:
        def rename_as_removed_if_exists(path: Path) -> None:
            if path.exists():
                path.rename(path.parent.joinpath(path.name + '.removed'))
        rename_as_removed_if_exists(self.main_output_file_path)
        rename_as_removed_if_exists(self.mcmc_output_file_path)
        rename_as_removed_if_exists(self.output_input_file_path)
        rename_as_removed_if_exists(self.path.joinpath('fit.lc_run_1'))
        rename_as_removed_if_exists(self.path.joinpath('resid.run_1'))

