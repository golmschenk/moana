import datetime
import math
import multiprocessing
import os
import re
import pandas as pd
from pathlib import Path

from moana.david_bennett_fit.fitting_algorithm_parameters import FittingAlgorithmParameters
from moana.david_bennett_fit.instrument_parameters import InstrumentParameters, MeasurementType
from moana.david_bennett_fit.light_curve_with_instrument_parameters import LightCurveWithInstrumentParameters
from moana.david_bennett_fit.run import Run
from moana.david_bennett_fit.runner import DavidBennettFitRunner
from moana.david_bennett_fit.lens_model_parameter import LensModelParameter
from moana.david_bennett_fit.names import LensModelParameterName
from moana.external_format_io.light_curve_file_liaison import LightCurveFileLiaison
from moana.light_curve import LightCurve as LightCurve, ColumnName

os.environ["DYLD_FALLBACK_LIBRARY_PATH"] = f"/Users/golmschenk/.conda/envs/moana/lib:{os.environ.get('DYLD_FALLBACK_LIBRARY_PATH')}"
print(os.environ.get('DYLD_FALLBACK_LIBRARY_PATH'))

print('Fitting script started.', flush=True)


def continue_existing_run(run_to_continue: Path):
    match = re.match(r'(.*)_[\d\-]+', run_to_continue.name)
    fit_run_name = f'{match.group(1)}'
    # fit_run_name = fit_run_name.replace('_mcmc0_continue2', '')
    fit_run_name += '_with_omega'
    datetime_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    fit_run_directory = Path(f'data/mb20208/runs/{fit_run_name}_{datetime_string}')
    fit_run_directory.mkdir(exist_ok=True, parents=True)
    event_light_curve_stem = 'lcMB20208'
    external_liaison = LightCurveFileLiaison()
    parameter_file_path = run_to_continue.joinpath('parMB20208')
    light_curve_without_parameters_list = LightCurve.list_for_run_directory(run_to_continue)
    light_curves = [
        LightCurveWithInstrumentParameters.from_light_curve_and_parameter_file(light_curve, parameter_file_path)
        for light_curve in light_curve_without_parameters_list]
    instrument_parameters_dictionary = InstrumentParameters.dictionary_from_david_bennett_parameter_file(
        parameter_file_path)
    lco1_instrument_parameters = instrument_parameters_dictionary['lco1']
    omega_g_light_curve_data_frame = external_liaison.load_omega_light_curve_data_frame(
        Path('data/mb20208/external_data/OMEGA_MOA_2020_BLG_208_gp.dat'))
    omega_g_instrument_parameters = InstrumentParameters(
        suffix='omegaG', measurement_type=MeasurementType.MAGNITUDE_21_BASED,
        earth_location=lco1_instrument_parameters.earth_location)
    omega_g_light_curve_with_parameters = LightCurveWithInstrumentParameters(
        'omegaG', omega_g_light_curve_data_frame, omega_g_instrument_parameters)
    light_curves.append(omega_g_light_curve_with_parameters)
    omega_i_light_curve_data_frame = external_liaison.load_omega_light_curve_data_frame(
        Path('data/mb20208/external_data/OMEGA_MOA_2020_BLG_208_ip.dat'))
    omega_i_instrument_parameters = InstrumentParameters(
        suffix='omegaI', measurement_type=MeasurementType.MAGNITUDE_21_BASED,
        earth_location=lco1_instrument_parameters.earth_location)
    omega_i_light_curve_with_parameters = LightCurveWithInstrumentParameters(
        'omegaI', omega_i_light_curve_data_frame, omega_i_instrument_parameters)
    light_curves.append(omega_i_light_curve_with_parameters)

    # for light_curve in light_curves:
    #     planetary_event_data_frame = light_curve.data_frame[
    #         (light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD.value] > 9112) &
    #         (light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD.value] < 9115)
    #         ]
    #     light_curve.remove_data_points_by_error_relative_to_maximum_minimum_range()
    #     chi_squared_mean = light_curve.remove_data_points_by_chi_squared_limit()
    #     light_curve.instrument_parameters.fudge_factor = \
    #         light_curve.instrument_parameters.fudge_factor * math.sqrt(chi_squared_mean)
    #     light_curve.data_frame = pd.concat([light_curve.data_frame, planetary_event_data_frame]).drop_duplicates()
    lens_model_parameter_dictionary = LensModelParameter.dictionary_from_lowest_chi_squared_from_mcmc_run_output(
        run_to_continue)
    # for lens_model_parameter_name, lens_model_parameter in lens_model_parameter_dictionary.items():
    #     if lens_model_parameter.temperature == 0:
    #         continue
    #     if lens_model_parameter_name == LensModelParameterName.MINIMUM_APPROACH_TIME.value:
    #         lens_model_parameter.temperature = 1e-6
    #     else:
    #         lens_model_parameter.temperature = lens_model_parameter.value * 1e-6
    fitting_algorithm_parameters = FittingAlgorithmParameters.from_david_bennett_parameter_file_path(
        parameter_file_path)
    david_bennett_fit_runner = DavidBennettFitRunner(fit_run_directory=fit_run_directory,
                                                     lens_model_parameter_dictionary=lens_model_parameter_dictionary,
                                                     light_curve_with_instrument_parameters_list=light_curves,
                                                     fitting_algorithm_parameters=fitting_algorithm_parameters)
    david_bennett_fit_runner.copy_mcmc_output_from_existing_run(Run(run_to_continue))
    print(f'Running `{fit_run_directory}` started at {datetime.datetime.now()}...', flush=True)
    david_bennett_fit_runner.calculate_residuals()
    print(f'Finished `{fit_run_directory}` at {datetime.datetime.now()}.', flush=True)


if __name__ == '__main__':
    continue_list = []
    for path in Path('data/mb20208/runs').glob('*'):
        if 'close_half' in path.name:
            continue_list.append(path)
    processes = []
    for to_continue in continue_list:
        process = multiprocessing.Process(target=continue_existing_run, args=(to_continue,))
        process.start()
        processes.append(process)
    for process in processes:
        process.join()
