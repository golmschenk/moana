"""
Code for representing instrument (telescope) parameters used in David Bennett's fitting code.
"""
from __future__ import annotations

import itertools
import re
from io import StringIO
import numpy as np
import pandas as pd
from enum import Enum
from pathlib import Path
from typing import Dict, Union, List

from astropy.coordinates import EarthLocation
from tabulate import tabulate


class MeasurementType(Enum):
    FLUX = 'flux'
    MAGNITUDE_0_BASED = 'magnitude_0_based'
    MAGNITUDE_21_BASED = 'magnitude_21_based'
    DEPRECATED = 'deprecated'


class InstrumentParameters:
    """
    A class representing instrument (telescope) parameters used in David Bennett's fitting code.
    """

    def __init__(self, suffix: str, measurement_type: MeasurementType, fudge_factor: float = 1.0,
                 time_offset: float = 0.0, earth_location: Union[EarthLocation, None] = None):
        self.suffix: str = suffix
        self.measurement_type: MeasurementType = measurement_type
        self.fudge_factor: float = fudge_factor
        self.time_offset: float = time_offset
        self.earth_location: EarthLocation = earth_location

    @classmethod
    def dictionary_from_david_bennett_parameter_file(cls, parameter_file_path: Path) -> Dict[str, InstrumentParameters]:
        """
        Loads the instrument parameters dictionary from David Bennett's parameter files.

        :param parameter_file_path: The path to the parameter file.
        :return: The dictionary of instrument paramters.
        """
        with parameter_file_path.open() as parameter_file:
            parameter_file_lines = parameter_file.readlines()
        while re.search(r'#\s+jclr', parameter_file_lines[0]) is None:  # If we haven't reached the second header...
            parameter_file_lines.pop(0)  # Remove the first line.
        parameter_file_lines.pop(0)  # Remove the header line, since it doesn't have a name for each column.
        parameters_content_string = ''.join(parameter_file_lines)
        parameters_string_io = StringIO(parameters_content_string)
        parameters_data_frame = pd.read_csv(
            parameters_string_io, header=None,
            names=['measurement_type_index', 'fudge_factor', 'error_minimum', 'flux_minimum', 'flux_maximum',
                   'limb_darkening_a', 'limb_darkening_b', 'time_offset', 'suffix', 'longitude', 'latitude'],
            delim_whitespace=True, skipinitialspace=True, quotechar="'"
        )
        instrument_parameters_dictionary = {}
        for index, parameters_row in parameters_data_frame.iterrows():
            measurement_type = cls.measurement_type_from_index(parameters_row['measurement_type_index'])
            if pd.notna(parameters_row['longitude']):
                earth_location = EarthLocation.from_geodetic(lon=parameters_row['longitude'],
                                                             lat=parameters_row['latitude'])
            else:
                earth_location = None
            instrument_parameters = cls(parameters_row['suffix'], measurement_type, parameters_row['fudge_factor'],
                                        parameters_row['time_offset'], earth_location)
            instrument_parameters_dictionary[instrument_parameters.suffix] = instrument_parameters
        return instrument_parameters_dictionary

    @classmethod
    def measurement_type_from_index(cls, index) -> MeasurementType:
        """
        Determines the types of measurement provided by a instrument based on it's measurement type index,
        often referred to as "jclr" in David Bennett's code.

        :param index:
        :return:
        """
        if index < 9:
            return MeasurementType.DEPRECATED
        elif 9 <= index <= 14:
            return MeasurementType.MAGNITUDE_0_BASED
        elif 15 <= index <= 29:
            return MeasurementType.MAGNITUDE_21_BASED
        elif 30 <= index <= 39:
            return MeasurementType.FLUX
        elif 40 <= index <= 49:
            return MeasurementType.MAGNITUDE_21_BASED
        elif 50 <= index <= 59:
            return MeasurementType.FLUX
        else:
            NotImplementedError(f'Instrument measurement type index (`jclr`) is not implemented for index {index}.')

    @classmethod
    def david_bennett_parameter_file_string_from_list(cls, instrument_parameters_list: List[InstrumentParameters]
                                                      ) -> str:
        parameter_data_frame = cls.create_instrument_parameter_data_frame_for_parameter_file(instrument_parameters_list)
        list_of_lists = parameter_data_frame.values.tolist()
        # noinspection PyTypeChecker
        list_of_lists = [[element for element in list_ if pd.notna(element)] for list_ in list_of_lists]
        file_string = tabulate(list_of_lists, tablefmt='plain', floatfmt='.10', headers=parameter_data_frame.columns)
        file_string = '# ' + file_string
        file_string = file_string.replace('\n', '\n  ')
        file_string = file_string.replace('longitude', '').replace('latitude', '')
        return file_string

    @classmethod
    def get_index_for_instrument_suffix(
            cls, instrument_suffix: str, instrument_parameters_list: List[InstrumentParameters]) -> int:
        data_frame = cls.create_instrument_parameter_data_frame_for_parameter_file(instrument_parameters_list)
        return data_frame[data_frame['sfx'] == f"'{instrument_suffix}'"]['jclr'].iloc[0]

    @classmethod
    def create_instrument_parameter_data_frame_for_parameter_file(
            cls, instrument_parameters_list: List[InstrumentParameters]) -> pd.DataFrame:
        measurement_type_index_generators = {
            MeasurementType.MAGNITUDE_0_BASED: iter(range(9, 15)),
            MeasurementType.MAGNITUDE_21_BASED: itertools.chain(range(15, 30), range(40, 50)),
            MeasurementType.FLUX: itertools.chain(range(30, 40), range(50, 60))
        }
        instrument_parameters_dictionary_list = []
        used_measurement_type_index = []
        for instrument_parameters in instrument_parameters_list:
            measurement_type_index = next(measurement_type_index_generators[instrument_parameters.measurement_type])
            if instrument_parameters.earth_location is not None:
                longitude = instrument_parameters.earth_location.lon.to_string(decimal=True)
                latitude = instrument_parameters.earth_location.lat.to_string(decimal=True)
            else:
                longitude = None
                latitude = None
            instrument_parameters_dictionary_list.append({
                'measurement_type_index': measurement_type_index,
                'fudge_factor': instrument_parameters.fudge_factor,
                'error_minimum': 0.003,
                'flux_minimum': -1.e9,
                'flux_maximum': 1.e9,
                'limb_darkening_a': 0.0,
                'limb_darkening_b': 0.0,
                'time_offset': instrument_parameters.time_offset,
                'suffix': f"'{instrument_parameters.suffix}'",
                'longitude': longitude,
                'latitude': latitude,
            })
            used_measurement_type_index.append(measurement_type_index)
        instrument_parameters_dictionary_list.sort(key=lambda entry: entry['measurement_type_index'])
        for filler_measurement_type_index in range(np.max(used_measurement_type_index)):
            if filler_measurement_type_index not in used_measurement_type_index:
                instrument_parameters_dictionary_list.append({
                    'measurement_type_index': filler_measurement_type_index,
                    'fudge_factor': 0,
                    'error_minimum': 0,
                    'flux_minimum': 0,
                    'flux_maximum': 0,
                    'limb_darkening_a': 0,
                    'limb_darkening_b': 0,
                    'time_offset': 0,
                    'suffix': 'null',
                    'longitude': 0,
                    'latitude': 0,
                })
        parameter_data_frame = pd.DataFrame(instrument_parameters_dictionary_list)
        parameter_data_frame = parameter_data_frame.astype({
            'measurement_type_index': int,
            'fudge_factor': float,
            'error_minimum': float,
            'flux_minimum': float,
            'flux_maximum': float,
            'limb_darkening_a': float,
            'limb_darkening_b': float,
            'time_offset': float,
            'suffix': str,
            'longitude': float,
            'latitude': float,
        })
        parameter_data_frame = parameter_data_frame.rename(columns={
            'measurement_type_index': 'jclr',
            'fudge_factor': 'fudge',
            'error_minimum': 'errmin',
            'flux_minimum': 'fmin',
            'flux_maximum': 'fmax',
            'limb_darkening_a': 'ald',
            'limb_darkening_b': 'bld',
            'time_offset': 'dayoff',
            'suffix': 'sfx',
        })
        return parameter_data_frame
