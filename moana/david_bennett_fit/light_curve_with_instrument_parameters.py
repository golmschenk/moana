import pandas as pd

from moana.david_bennett_fit.instrument_parameters import InstrumentParameters
from moana.light_curve import LightCurve


class LightCurveWithInstrumentParameters(LightCurve):
    def __init__(self, instrument_suffix: str, data_frame: pd.DataFrame, instrument_parameters: InstrumentParameters):
        super().__init__(instrument_suffix, data_frame)
        self.instrument_parameters: InstrumentParameters = instrument_parameters
