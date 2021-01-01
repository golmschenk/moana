import datetime
import re
import pandas as pd
from pathlib import Path

from moana.david_bennett_fit.runner import DavidBennettFitRunner
from moana.david_bennett_fit.lens_model_parameter import LensModelParameter
from moana.external_format_io.light_curve_file_liaison import LightCurveFileLiaison
from moana.light_curve import LightCurve as LightCurve, ColumnName

print('Fitting script started.', flush=True)

moa_instruments = 'moa'
more_instruments = 'more_instruments'
run_to_continue = Path('data/mb20208/runs/wide_detailed_more_instruments_parallax_2020-12-23-17-59-02')
instruments = more_instruments

match = re.match(r'(.*)_[\d\-]+', run_to_continue.name)
fit_run_name = f'{match.group(1)}_data_cleaned'
datetime_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
fit_run_directory = Path(f'data/mb20208/runs/{fit_run_name}_{datetime_string}')
fit_run_directory.mkdir(exist_ok=True, parents=True)

event_light_curve_stem = 'lcMB20208'
external_liaison = LightCurveFileLiaison()

light_curves = LightCurve.list_for_run_directory_with_residuals(run_to_continue)
for light_curve in light_curves:
    planetary_event_data_frame = light_curve.data_frame[
        (light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD] > 9112) &
        (light_curve.data_frame[ColumnName.TIME__MICROLENSING_HJD] < 9115)
    ]
    light_curve.remove_data_points_by_error_relative_to_maximum_minimum_range()
    light_curve.remove_data_points_by_chi_squared_limit()
    light_curve.data_frame = pd.concat([light_curve.data_frame, planetary_event_data_frame]).drop_duplicates()
LightCurve.save_list_to_directory(fit_run_directory)

# moa2r_light_curve_data_frame = external_liaison.load_ian_bond_light_curve(
#     Path('data/mb20208/external_data/mb20208-MOA2R-10000.phot.dat'))
# moa2v_light_curve_data_frame = external_liaison.load_ian_bond_light_curve(
#     Path('data/mb20208/external_data/mb20208-MOA2V-10000.phot.dat'))
# if instruments == more_instruments:
#     kmtA22_light_curve_data_frame = external_liaison.load_kmt_tlc_light_curve(
#         Path('data/mb20208/external_data/KMTA22_I.pysis.dflux'))
#     kmtA22_light_curve_data_frame = kmtA22_light_curve_data_frame[
#         kmtA22_light_curve_data_frame[ColumnName.FULL_WIDTH_HALF_MAX.value] != 1]
#     kmtA22_light_curve_data_frame = kmtA22_light_curve_data_frame[
#         kmtA22_light_curve_data_frame[ColumnName.FULL_WIDTH_HALF_MAX.value] < 7]
#     lco1_light_curve_data_frame = external_liaison.load_lco_light_curve(
#         Path('data/mb20208/external_data/MB20208_cpt01.mag')
#     )
#     kko_light_curve_data_frame = external_liaison.load_dophot_light_curve(
#         Path('data/mb20208/external_data/KKO_MB20208U.pho')
#     )
#     pest_light_curve_data_frame = external_liaison.load_dophot_light_curve(
#         Path('data/mb20208/external_data/PEST_MB20208U.pho')
#     )
#     pos_light_curve_data_frame = external_liaison.load_dophot_light_curve(
#         Path('data/mb20208/external_data/Pos_MB20208U.pho')
#     )
#     tur_light_curve_data_frame = external_liaison.load_dophot_light_curve(
#         Path('data/mb20208/external_data/Tur_MB20208R.pho')
#     )
# light_curve_data_frames = [moa2r_light_curve_data_frame, moa2v_light_curve_data_frame]
# if instruments == more_instruments:
#     light_curve_data_frames.extend([kmtA22_light_curve_data_frame, lco1_light_curve_data_frame,
#                                     kko_light_curve_data_frame, pest_light_curve_data_frame,
#                                     pos_light_curve_data_frame, tur_light_curve_data_frame])
# for light_curve_data_frame in light_curve_data_frames:
#     light_curve_data_frame.drop(
#         light_curve_data_frame[light_curve_data_frame[ColumnName.MICROLENSING_HJD.value] < 9000].index, inplace=True)
#     light_curve_data_frame.drop(
#         light_curve_data_frame[light_curve_data_frame[ColumnName.MICROLENSING_HJD.value] > 9200].index, inplace=True)
# LightCurve.save_light_curve_to_david_bennett_format_file(
#     fit_run_directory.joinpath(f'{event_light_curve_stem}.moa2r'), moa2r_light_curve_data_frame)
# LightCurve.save_light_curve_to_david_bennett_format_file(
#     fit_run_directory.joinpath(f'{event_light_curve_stem}.moa2v'), moa2v_light_curve_data_frame)
# if instruments == more_instruments:
#     LightCurve.save_light_curve_to_david_bennett_format_file(
#         fit_run_directory.joinpath(f'{event_light_curve_stem}.kmtA22'), kmtA22_light_curve_data_frame)
#     LightCurve.save_light_curve_to_david_bennett_format_file(
#         fit_run_directory.joinpath(f'{event_light_curve_stem}.lco1'), lco1_light_curve_data_frame)
#     LightCurve.save_light_curve_to_david_bennett_format_file(
#         fit_run_directory.joinpath(f'{event_light_curve_stem}.kko'), kko_light_curve_data_frame)
#     LightCurve.save_light_curve_to_david_bennett_format_file(
#         fit_run_directory.joinpath(f'{event_light_curve_stem}.pos'), pos_light_curve_data_frame)
#     LightCurve.save_light_curve_to_david_bennett_format_file(
#         fit_run_directory.joinpath(f'{event_light_curve_stem}.tur'), tur_light_curve_data_frame)

# lens_model_parameter_dictionary = {
#     'v_sep':  LensModelParameter(value=1, temperature=3),
#     '1/t_E':  LensModelParameter(value=1, temperature=3),
#     't0':     LensModelParameter(value=1, temperature=3),
#     'umin':   LensModelParameter(value=1, temperature=3),
#     'theta':  LensModelParameter(value=1, temperature=3),
#     'eps1':   LensModelParameter(value=1, temperature=3),
#     '1/Tbin': LensModelParameter(value=1, temperature=1e-8),
#     'sep':    LensModelParameter(value=1, temperature=3, minimum_limit=0, maximum_limit=4),
#     'Tstar':  LensModelParameter(value=1, temperature=3),
#     't_fix':  LensModelParameter(value=1, temperature=3, minimum_limit=1e-7, maximum_limit=1e2),
#     'piEr':   LensModelParameter(value=1, temperature=3),
#     'pieth':  LensModelParameter(value=1, temperature=3)
# }

lens_model_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(
    run_to_continue.joinpath('run_2.in')
)

david_bennett_fit_runner = DavidBennettFitRunner(fit_run_directory=fit_run_directory,
                                                 lens_model_parameter_dictionary=lens_model_parameter_dictionary)
david_bennett_fit_runner.generate_configuration_files()

print(f'Running `{fit_run_directory}` started at {datetime.datetime.now()}...', flush=True)
david_bennett_fit_runner.run()
print(f'Finished `{fit_run_directory}` at {datetime.datetime.now()}.', flush=True)
