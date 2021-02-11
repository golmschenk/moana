"""
Code to represent an existing run.
"""
from __future__ import annotations

from pathlib import Path
from typing import Optional

from moana.dbc import Output


class Run:
    """
    A class to represent an existing run.
    """
    def __init__(self, path: Path, input_file_name: str = 'run_1.in', output_input_file_name: str = 'run_2.in',
                 display_name: Optional[str] = None):
        self.path: Path = path
        self.input_file_name: str = input_file_name
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
    def dbc_output(self) -> Output:
        if self._dbc_output is None:
            self._dbc_output = Output(run=self.input_file_name[:-3], path=str(self.path))
            self._dbc_output.load()
        return self._dbc_output
