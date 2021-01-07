import datetime
import re
import pandas as pd
from pathlib import Path

from moana.david_bennett_fit.fitting_algorithm_parameters import FittingAlgorithmParameters
from moana.david_bennett_fit.light_curve_with_instrument_parameters import LightCurveWithInstrumentParameters
from moana.david_bennett_fit.runner import DavidBennettFitRunner
from moana.david_bennett_fit.lens_model_parameter import LensModelParameter
from moana.external_format_io.light_curve_file_liaison import LightCurveFileLiaison
from moana.light_curve import LightCurve as LightCurve, ColumnName

print('Fitting script started.', flush=True)

run_to_continue = Path('data/mb20208/runs/close_detailed_moa_2020-12-28-16-00-33')

match = re.match(r'(.*)_[\d\-]+', run_to_continue.name)
fit_run_name = f'{match.group(1)}_check'
datetime_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
fit_run_directory = Path(f'data/mb20208/runs/{fit_run_name}_{datetime_string}')
fit_run_directory.mkdir(exist_ok=True, parents=True)

event_light_curve_stem = 'lcMB20208'
external_liaison = LightCurveFileLiaison()
parameter_file_path = run_to_continue.joinpath('parMB20208')

light_curve_without_parameters_list = LightCurve.list_for_run_directory_with_residuals(run_to_continue)
light_curves = [LightCurveWithInstrumentParameters.from_light_curve_and_parameter_file(light_curve, parameter_file_path)
                for light_curve in light_curve_without_parameters_list]
for light_curve in light_curves:
    planetary_event_data_frame = light_curve.data_frame[
        (light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD.value] > 9112) &
        (light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD.value] < 9115)
    ]
    light_curve.remove_data_points_by_error_relative_to_maximum_minimum_range()
    light_curve.remove_data_points_by_chi_squared_limit()
    light_curve.data_frame = pd.concat([light_curve.data_frame, planetary_event_data_frame]).drop_duplicates()
LightCurve.save_list_to_directory(light_curves, fit_run_directory)

lens_model_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(
    run_to_continue.joinpath('run_2.in')
)

fitting_algorithm_parameters = FittingAlgorithmParameters.from_david_bennett_parameter_file_path(parameter_file_path)

david_bennett_fit_runner = DavidBennettFitRunner(fit_run_directory=fit_run_directory,
                                                 lens_model_parameter_dictionary=lens_model_parameter_dictionary,
                                                 light_curve_with_instrument_parameters_list=light_curves,
                                                 fitting_algorithm_parameters=fitting_algorithm_parameters)
david_bennett_fit_runner.generate_configuration_files()

print(f'Running `{fit_run_directory}` started at {datetime.datetime.now()}...', flush=True)
david_bennett_fit_runner.run()
print(f'Finished `{fit_run_directory}` at {datetime.datetime.now()}.', flush=True)
