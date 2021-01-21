from pathlib import Path
from typing import List

from moana.david_bennett_fit.instrument_parameters import InstrumentParameters
from moana.david_bennett_fit.light_curve_with_instrument_parameters import LightCurveWithInstrumentParameters
from moana.external_format_io.light_curve_file_liaison import LightCurveFileLiaison
from moana.light_curve import ColumnName


def create_all_mb20208_light_curves() -> List[LightCurveWithInstrumentParameters]:
    external_liaison = LightCurveFileLiaison()
    light_curves: List[LightCurveWithInstrumentParameters] = []
    instrument_parameters_dictionary = InstrumentParameters.dictionary_from_david_bennett_parameter_file(
        Path('data/mb20208/template/parMB20208'))

    moa2r_light_curve_data_frame = external_liaison.load_ian_bond_light_curve(
        Path('data/mb20208/external_data/mb20208-MOA2R-10000.phot.dat'))
    moa2r_suffix = 'moa2r'
    moa2r_light_curve = LightCurveWithInstrumentParameters(
        moa2r_suffix, moa2r_light_curve_data_frame, instrument_parameters_dictionary[moa2r_suffix])
    light_curves.append(moa2r_light_curve)

    moa2v_light_curve_data_frame = external_liaison.load_ian_bond_light_curve(
        Path('data/mb20208/external_data/mb20208-MOA2V-10000.phot.dat'))
    moa2v_suffix = 'moa2v'
    moa2v_light_curve = LightCurveWithInstrumentParameters(
        moa2v_suffix, moa2v_light_curve_data_frame, instrument_parameters_dictionary[moa2v_suffix])
    light_curves.append(moa2v_light_curve)

    kmtA22_light_curve_data_frame = external_liaison.load_kmt_tlc_light_curve(
        Path('data/mb20208/external_data/KMTA22_I.pysis.dflux'))
    kmtA22_light_curve_data_frame = kmtA22_light_curve_data_frame[
        kmtA22_light_curve_data_frame[ColumnName.FULL_WIDTH_HALF_MAX.value] != 1]
    kmtA22_light_curve_data_frame = kmtA22_light_curve_data_frame[
        kmtA22_light_curve_data_frame[ColumnName.FULL_WIDTH_HALF_MAX.value] < 7]
    kmtA22_suffix = 'kmtA22'
    kmtA22_light_curve = LightCurveWithInstrumentParameters(
        kmtA22_suffix, kmtA22_light_curve_data_frame, instrument_parameters_dictionary[kmtA22_suffix])
    light_curves.append(kmtA22_light_curve)

    dophot_file_dictionary = {'kko': 'KKO_MB20208U.pho',
                              'pest': 'PEST_MB20208U.pho',
                              'pos': 'Pos_MB20208U.pho',
                              'pos35': 'Pos35_MB20208U.pho',
                              'tur': 'Tur_MB20208R.pho'}
    for suffix, file_name in dophot_file_dictionary.items():
        data_frame = external_liaison.load_dophot_light_curve(Path(f'data/mb20208/external_data/{file_name}'))
        light_curves.append(
            LightCurveWithInstrumentParameters(suffix, data_frame, instrument_parameters_dictionary[suffix]))

    lco1_light_curve_data_frame = external_liaison.load_lco_light_curve(
            Path('data/mb20208/external_data/MB20208_cpt01.mag'))
    lco1_suffix = 'lco1'
    lco1_light_curve = LightCurveWithInstrumentParameters(
        lco1_suffix, lco1_light_curve_data_frame, instrument_parameters_dictionary[lco1_suffix])
    light_curves.append(lco1_light_curve)

    pysis_file_dictionary = {'kumeu': 'Kumeu_MB20208R.pysis',
                             'auck': 'Auckland_MB20208R.pysis',
                             'fco': 'FCO_MB20208U.pysis'}
    for suffix, file_name in pysis_file_dictionary.items():
        data_frame = external_liaison.load_pysis_light_curve_data_frame(Path(f'data/mb20208/external_data/{file_name}'))
        light_curves.append(
            LightCurveWithInstrumentParameters(suffix, data_frame, instrument_parameters_dictionary[suffix]))
        
    for light_curve in light_curves:
        light_curve.data_frame.drop(
            light_curve.data_frame[light_curve.data_frame[ColumnName.MICROLENSING_HJD.value] < 9000].index, inplace=True)
        light_curve.data_frame.drop(
            light_curve.data_frame[light_curve.data_frame[ColumnName.MICROLENSING_HJD.value] > 9200].index, inplace=True)

    return light_curves
