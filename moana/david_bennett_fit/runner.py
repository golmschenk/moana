"""
Code to manage fitting runs using David Bennett's code.
"""
import shutil
import datetime
import subprocess
from pathlib import Path
from typing import Dict

from moana.david_bennett_fit.lens_model_parameter import LensModelParameter


class DavidBennettFitRunner:
    """
    A class to manage fitting runs using David Bennett's code.
    """
    def __init__(self, fit_run_directory: Path, lens_model_parameter_dictionary: Dict[str, LensModelParameter]):
        self.fit_run_directory = fit_run_directory
        self.lens_model_parameter_dictionary = lens_model_parameter_dictionary

    def generate_configuration_files(self):
        """
        Generates the files required to run David Bennett's fitting code.

        :return: The path to the fit run directory.
        """
        self.fit_run_directory.mkdir(exist_ok=True, parents=True)
        self.generate_david_bennett_parameter_file()
        self.generate_david_bennett_run_input_file()

    def generate_david_bennett_parameter_file(self):
        existing_parameter_file = Path('data/mb20208/template/parMB20208')
        shutil.copy(existing_parameter_file, self.fit_run_directory.joinpath('parMB20208'))
        # TODO: Generate this from script variables rather than just copying an existing one.

    def generate_david_bennett_run_input_file(self):
        datetime_string = datetime.datetime.now()
        comment_line = f'Auto-generated on {datetime_string}.\n'
        lens_model_parameter_lines = LensModelParameter.david_bennett_input_string_from_dictionary(
            self.lens_model_parameter_dictionary)
        blank_line = f'\n\n'
        # TODO: Set the below lines by the user script rather than hard coded.
        run_configuration_lines = 'MB20208\n' \
                                  'run_\n' \
                                  'no limb\n' \
                                  '17 53 43.80 -32 35 21.52\n' \
                                  '0\n'
        instruction_lines = 'SET EPS   1.e-5\n' \
                            'DSEEK      3000\n' \
                            'SET ERR     0.2\n' \
                            'DSEEK      3000\n' \
                            'EXIT\n'
        input_file_path = self.fit_run_directory.joinpath('run_1.in')
        with input_file_path.open('w') as input_file:
            input_file.write(comment_line + lens_model_parameter_lines + blank_line + run_configuration_lines +
                             instruction_lines)

    def run(self):
        path_to_bennett_fitting_executable = Path('fit_rvg4_CRtpar/minuit_all_rvg4Ctpar.xO').absolute()

        run_path = self.fit_run_directory.joinpath('run_1.in')

        run_name = run_path.stem
        working_directory = run_path.parent

        input_path = working_directory.joinpath(f'{run_name}.in')
        output_path = working_directory.joinpath(f'{run_name}.out')

        subprocess.run(str(path_to_bennett_fitting_executable), cwd=working_directory, stdin=input_path.open('r'),
                       stdout=output_path.open('w'), stderr=subprocess.STDOUT)

        self.lens_model_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(
            self.fit_run_directory.joinpath('run_2.in'))
