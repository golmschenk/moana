from __future__ import annotations

import pandas as pd
from pathlib import Path

from moana.david_bennett_fit.instrument_parameters import InstrumentParameters
from moana.light_curve import LightCurve


class LightCurveWithInstrumentParameters(LightCurve):
    def __init__(self, instrument_suffix: str, data_frame: pd.DataFrame, instrument_parameters: InstrumentParameters):
        super().__init__(instrument_suffix, data_frame)
        self.instrument_parameters: InstrumentParameters = instrument_parameters

    @classmethod
    def from_light_curve_and_parameter_file(cls, light_curve: LightCurve, parameter_file_path: Path
                                            ) -> LightCurveWithInstrumentParameters:
        instrument_parameters_dictionary = InstrumentParameters.dictionary_from_david_bennett_parameter_file(
            parameter_file_path)
        instrument_parameters = instrument_parameters_dictionary[light_curve.instrument_suffix]
        return cls(light_curve.instrument_suffix, light_curve.data_frame, instrument_parameters)
