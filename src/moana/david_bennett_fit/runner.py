"""
Code to manage fitting runs using David Bennett's code.
"""
import datetime
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Type

from moana.david_bennett_fit.fitting_algorithm_parameters import FittingAlgorithmParameters
from moana.david_bennett_fit.instrument_parameters import InstrumentParameters
from moana.david_bennett_fit.lens_model_parameter import LensModelParameter
from moana.david_bennett_fit.light_curve_with_instrument_parameters import LightCurveWithInstrumentParameters
from moana.david_bennett_fit.names import LensModelParameterNameEnum, BinaryLensModelParameterNameEnum, \
    BinarySourceModelParameterNameEnum
from moana.david_bennett_fit.run import Run
from moana.light_curve import LightCurve


class DavidBennettFitRunner:
    """
    A class to manage fitting runs using David Bennett's code.
    """

    def __init__(self, fit_run_directory: Path, lens_model_parameter_dictionary: Dict[str, LensModelParameter],
                 light_curve_with_instrument_parameters_list: List[LightCurveWithInstrumentParameters],
                 fitting_algorithm_parameters: FittingAlgorithmParameters,
                 lens_parameter_name_enum: Type[LensModelParameterNameEnum] = BinaryLensModelParameterNameEnum):
        self.fit_run_directory: Path = fit_run_directory
        self.run = Run(fit_run_directory)
        self.lens_model_parameter_dictionary: Dict[str, LensModelParameter] = lens_model_parameter_dictionary
        self.light_curve_with_instrument_parameters_list: List[LightCurveWithInstrumentParameters] = \
            light_curve_with_instrument_parameters_list
        self.fitting_algorithm_parameters: FittingAlgorithmParameters = fitting_algorithm_parameters
        self.instructions: Optional[str] = None
        self.lens_parameter_name_enum: Type[LensModelParameterNameEnum] = lens_parameter_name_enum
        self.david_bennett_fitting_executable_path: Path = Path(
            'david_bennett_fitting/radial_version/minuit_all_rvg4Rtpar.xO')

    def generate_run_files(self):
        """
        Generates the files required to run David Bennett's fitting code.

        :return: The path to the fit run directory.
        """
        self.fit_run_directory.mkdir(exist_ok=True, parents=True)
        self.generate_david_bennett_parameter_file()
        self.generate_david_bennett_run_input_file()
        LightCurve.save_list_to_directory(self.light_curve_with_instrument_parameters_list, self.fit_run_directory)

    def generate_david_bennett_parameter_file(self):
        parameter_file_path = self.fit_run_directory.joinpath('parMB20208')
        with open(parameter_file_path, 'w') as parameter_file:
            parameter_file.write(self.fitting_algorithm_parameters.to_david_bennett_parameter_file_string())
            parameter_file.write('\n')
            instrument_parameters_list = [light_curve.instrument_parameters
                                          for light_curve in self.light_curve_with_instrument_parameters_list]
            parameter_file.write(
                InstrumentParameters.david_bennett_parameter_file_string_from_list(instrument_parameters_list))

    def generate_david_bennett_run_input_file(self):
        datetime_string = datetime.datetime.now()
        comment_line = f'Auto-generated on {datetime_string}.\n'
        lens_model_parameter_lines = LensModelParameter.david_bennett_input_string_from_dictionary(
            self.lens_model_parameter_dictionary, lens_parameter_name_enum=self.lens_parameter_name_enum)
        blank_line = f'\n\n'
        run_configuration_lines = self.generate_run_configuration_lines()
        input_file_path = self.fit_run_directory.joinpath('run_1.in')
        with input_file_path.open('w') as input_file:
            input_file.write(comment_line + lens_model_parameter_lines + blank_line + run_configuration_lines +
                             self.instructions)

    def generate_run_configuration_lines(self):
        # TODO: Set the below lines by the user script rather than hard coded.
        run_configuration_lines = 'MB20208\n' \
                                  'run_\n' \
                                  'no limb\n' \
                                  '17 53 43.80 -32 35 21.52\n'
        if self.lens_parameter_name_enum == BinarySourceModelParameterNameEnum:
            instrument_parameters = [light_curve.instrument_parameters
                                     for light_curve in self.light_curve_with_instrument_parameters_list]
            moa_r_parameter_index = InstrumentParameters.get_index_for_instrument_suffix('moa2r', instrument_parameters)
            moa_v_parameter_index = InstrumentParameters.get_index_for_instrument_suffix('moa2v', instrument_parameters)
            run_configuration_lines += f'{moa_r_parameter_index} {moa_v_parameter_index} 7.1 0.040308 0.003181 ' \
                                        '0.223948 0.911340 1.580 2.995  200 1 1\n'
        run_configuration_lines += f'0 {"mcmc_run_1.dat" if "OSEEK" in self.instructions else ""}\n'
        return run_configuration_lines

    def run_algorithm(self):
        path_to_bennett_fitting_executable = self.david_bennett_fitting_executable_path.absolute()

        run_path = self.fit_run_directory.joinpath('run_1.in')

        run_name = run_path.stem
        working_directory = run_path.parent

        input_path = working_directory.joinpath(f'{run_name}.in')
        output_path = working_directory.joinpath(f'{run_name}.out')

        subprocess.run(str(path_to_bennett_fitting_executable), cwd=working_directory, stdin=input_path.open('r'),
                       stdout=output_path.open('w'), stderr=subprocess.STDOUT)

        LensModelParameter.reformat_parameters_in_david_bennett_input_file(self.fit_run_directory.joinpath('run_2.in'))
        self.lens_model_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(
            self.fit_run_directory.joinpath('run_2.in'), lens_parameter_name_enum=self.lens_parameter_name_enum)

    def calculate_residuals(self):
        self.instructions = 'SET EPS   1.e-5\n' \
                            'SET ERR     0.2\n' \
                            'EXIT\n'
        self.generate_run_files()
        self.run_algorithm()

    def fit(self):
        self.instructions = 'SET EPS   1.e-5\n' \
                            'DSEEK      6000\n' \
                            'SET ERR     0.2\n' \
                            'DSEEK      6000\n' \
                            'EXIT\n'
        self.generate_run_files()
        self.run_algorithm()

    def mcmc(self, steps_to_run: int = int(2e6), use_covariance: bool = False,
             rows_to_include_in_covariance: Optional[int] = None, rows_to_exclude_in_covariance: Optional[int] = None):
        covariance_string = ''
        if use_covariance:
            assert rows_to_include_in_covariance is None or rows_to_exclude_in_covariance is None
            total_rows = self.run.get_mcmc_output_file_row_count()
            if rows_to_include_in_covariance is not None:
                assert rows_to_include_in_covariance <= total_rows
                rows_to_delete = total_rows - rows_to_include_in_covariance
            elif rows_to_exclude_in_covariance is not None:
                assert rows_to_exclude_in_covariance < total_rows
                rows_to_delete = rows_to_exclude_in_covariance
            else:
                raise ValueError('When using covariance, either rows to exclude or include must be specified.')
            total_rows = self.run.get_mcmc_output_file_row_count()
            covariance_string = f'2.3 0.7 {rows_to_delete} {total_rows}'
        else:
            assert rows_to_include_in_covariance is None and rows_to_exclude_in_covariance is None
        if self.run.mcmc_output_file_path.exists():
            existing_steps = self.run.get_mcmc_output_file_state_count()
            steps_to_run -= existing_steps
        if steps_to_run < 1:
            print('MCMC output already has desired steps.')
            return
        self.instructions = 'SET EPS 1.e-5\n' \
                            'SET ERR 2.0\n' \
                            f'OSEEK {steps_to_run} {covariance_string}\n' \
                            'EXIT\n'
        self.generate_run_files()
        self.run_algorithm()

    def copy_mcmc_output_from_existing_run(self, existing_run: Run):
        if self.run.mcmc_output_file_path.exists():
            raise IOError('MCMC output file already exists.')
        else:
            shutil.copyfile(existing_run.mcmc_output_file_path, self.run.mcmc_output_file_path)
