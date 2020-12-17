import datetime
from pathlib import Path

from moana.david_bennett_fit.runner import DavidBennettFitRunner
from moana.david_bennett_fit.lens_model_parameter import LensModelParameter, LensModelParameterName
from moana.external_format_io.light_curve_file_liaison import LightCurveFileLiaison, ColumnNames
from moana.david_bennett_fit.light_curve import LightCurveFileLiaison as DbLightCurveFileLiaison

fit_run_name = 'far_detailed_more_instruments'
datetime_string = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
fit_run_directory = Path(f'data/mb20208/runs/{fit_run_name}_{datetime_string}')
fit_run_directory.mkdir(exist_ok=True, parents=True)

event_light_curve_stem = 'lcMB20208'
external_liaison = LightCurveFileLiaison()
david_bennett_liaison = DbLightCurveFileLiaison()
moa2r_light_curve_data_frame = external_liaison.load_ian_bond_light_curve(
    Path('data/mb20208/external_data/mb20208-MOA2R-10000.phot.dat'))
moa2v_light_curve_data_frame = external_liaison.load_ian_bond_light_curve(
    Path('data/mb20208/external_data/mb20208-MOA2V-10000.phot.dat'))
kmtA22_light_curve_data_frame = external_liaison.load_kmt_tlc_light_curve(
    Path('data/mb20208/external_data/KMTA22_I.pysis.dflux'))
kmtA22_light_curve_data_frame = kmtA22_light_curve_data_frame[
    kmtA22_light_curve_data_frame[ColumnNames.FULL_WIDTH_HALF_MAX.value] != 1]
kmtA22_light_curve_data_frame = kmtA22_light_curve_data_frame[
    kmtA22_light_curve_data_frame[ColumnNames.FULL_WIDTH_HALF_MAX.value] < 7]
lco1_light_curve_data_frame = external_liaison.load_lco_light_curve(
    Path('data/mb20208/external_data/MB20208_cpt01.mag')
)
kko_light_curve_data_frame = external_liaison.load_dophot_light_curve(
    Path('data/mb20208/external_data/KKO_MB20208U.pho')
)
pest_light_curve_data_frame = external_liaison.load_dophot_light_curve(
    Path('data/mb20208/external_data/PEST_MB20208U.pho')
)
pos_light_curve_data_frame = external_liaison.load_dophot_light_curve(
    Path('data/mb20208/external_data/Pos_MB20208U.pho')
)
tur_light_curve_data_frame = external_liaison.load_dophot_light_curve(
    Path('data/mb20208/external_data/Tur_MB20208R.pho')
)
light_curve_data_frames = [moa2r_light_curve_data_frame, moa2v_light_curve_data_frame, kmtA22_light_curve_data_frame,
                           lco1_light_curve_data_frame, kko_light_curve_data_frame, pest_light_curve_data_frame,
                           pos_light_curve_data_frame, tur_light_curve_data_frame]
for light_curve_data_frame in light_curve_data_frames:
    light_curve_data_frame.drop(
        light_curve_data_frame[light_curve_data_frame[ColumnNames.MICROLENSING_HJD.value] < 9050].index, inplace=True)
    light_curve_data_frame.drop(
        light_curve_data_frame[light_curve_data_frame[ColumnNames.MICROLENSING_HJD.value] > 9150].index, inplace=True)
david_bennett_liaison.save_light_curve_to_david_bennett_format_file(
    fit_run_directory.joinpath(f'{event_light_curve_stem}.moa2r'), moa2r_light_curve_data_frame)
david_bennett_liaison.save_light_curve_to_david_bennett_format_file(
    fit_run_directory.joinpath(f'{event_light_curve_stem}.moa2v'), moa2v_light_curve_data_frame)
david_bennett_liaison.save_light_curve_to_david_bennett_format_file(
    fit_run_directory.joinpath(f'{event_light_curve_stem}.kmtA22'), kmtA22_light_curve_data_frame)
david_bennett_liaison.save_light_curve_to_david_bennett_format_file(
    fit_run_directory.joinpath(f'{event_light_curve_stem}.lco1'), lco1_light_curve_data_frame)
david_bennett_liaison.save_light_curve_to_david_bennett_format_file(
    fit_run_directory.joinpath(f'{event_light_curve_stem}.kko'), kko_light_curve_data_frame)
david_bennett_liaison.save_light_curve_to_david_bennett_format_file(
    fit_run_directory.joinpath(f'{event_light_curve_stem}.pos'), pos_light_curve_data_frame)
david_bennett_liaison.save_light_curve_to_david_bennett_format_file(
    fit_run_directory.joinpath(f'{event_light_curve_stem}.tur'), tur_light_curve_data_frame)

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
    Path('data/mb20208/runs/moa_detailed_far_2020_11_24/run_2.in')
)

path = Path('data/mb20208/runs/moa_detailed_far_2020_11_24/run_2.in')
# lens_model_parameter_dictionary[LensModelParameterName.PI_ER.value].temperature = 1e-5
# lens_model_parameter_dictionary[LensModelParameterName.PI_ETH.value].temperature = 1e-5

david_bennett_fit_runner = DavidBennettFitRunner(fit_run_directory=fit_run_directory,
                                                 lens_model_parameter_dictionary=lens_model_parameter_dictionary)
david_bennett_fit_runner.generate_configuration_files()

print(f'Running `{fit_run_directory}` started at {datetime.datetime.now()}...')
david_bennett_fit_runner.run()
print(f'Finished `{fit_run_directory}` at {datetime.datetime.now()}.')
