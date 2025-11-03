from typing import List

from moana.david_bennett_fit.run import Run
from moana.dbc import Output


class RunModifier:
    def limit_date_range(self, run: Output, lower: float, upper: float):
        run.resid = run.resid[(lower < run.resid['date']) & (run.resid['date'] < upper)]
        run.fitlc = run.fitlc[(lower < run.fitlc['date']) & (run.fitlc['date'] < upper)]

    def remove_instrument_suffix(self, run: Run, suffix: str):
        run.dbc_output.resid = run.dbc_output.resid[run.dbc_output.resid['sfx'] != suffix]

    def used_only_single_instrument_suffix(self, run: Run, suffix: str):
        run.dbc_output.resid = run.dbc_output.resid[run.dbc_output.resid['sfx'] == suffix]

    def filter_instrument_suffixes_to_keep(self, run: Run, suffixes: List[str]):
        run.dbc_output.resid = run.dbc_output.resid[run.dbc_output.resid['sfx'].isin(suffixes)]

    def filter_instrument_suffixes_to_keep(self, run: Run, suffixes: List[str]):
        run.dbc_output.resid = run.dbc_output.resid[run.dbc_output.resid['sfx'].isin(suffixes)]