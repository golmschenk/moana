"""
Code to represent an existing run.
"""
from __future__ import annotations

import pandas as pd
from pathlib import Path
from typing import Optional, List

from moana.david_bennett_fit.names import LensModelParameterName
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
        run0.display_name = '_'.join(split_display_name0)
        run1.display_name = '_'.join(split_display_name1)

    @property
    def mcmc_output_file_path(self) -> Path:
        return self.path.joinpath('mcmc_run_1.dat')

    def get_mcmc_output_file_state_count(self) -> int:
        state_repeat_column_index = 17
        mcmc_output_dataframe = pd.read_csv(self.mcmc_output_file_path, delim_whitespace=True, skipinitialspace=True,
                                            header=None, index_col=None, usecols=[state_repeat_column_index])
        return mcmc_output_dataframe[state_repeat_column_index].sum()

    def get_mcmc_output_file_row_count(self) -> int:
        state_repeat_column_index = 17
        mcmc_output_dataframe = pd.read_csv(self.mcmc_output_file_path, delim_whitespace=True, skipinitialspace=True,
                                            header=None, index_col=None, usecols=[state_repeat_column_index])
        return mcmc_output_dataframe[state_repeat_column_index].shape[0]

    def load_minimum_chi_squared_mcmc_output_state(self) -> pd.Series:
        mcmc_output_dataframe = self.load_mcmc_output_states()
        minimum_chi_squared_lens_parameter_row = mcmc_output_dataframe.iloc[
            mcmc_output_dataframe[FitModelColumnName.CHI_SQUARED.value].argmin()]
        return minimum_chi_squared_lens_parameter_row

    def load_mcmc_output_states(self) -> pd.DataFrame:
        mcmc_output_dataframe = pd.read_csv(self.mcmc_output_file_path, delim_whitespace=True, skipinitialspace=True,
                                            header=None, index_col=None)
        lens_model_parameter_names = [name.value for name in LensModelParameterName]
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
