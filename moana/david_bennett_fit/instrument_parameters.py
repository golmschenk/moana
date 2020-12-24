"""
Code for representing instrument (telescope) parameters used in David Bennett's fitting code.
"""
from __future__ import annotations

import re
from io import StringIO
import pandas as pd
from enum import Enum
from pathlib import Path
from typing import Dict, Union

from astropy.coordinates import EarthLocation


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
