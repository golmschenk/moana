from moana.dbc import Output


class RunModifier:
    def limit_date_range(self, run: Output, lower: float, upper: float):
        run.resid = run.resid[(lower < run.resid['date']) & (run.resid['date'] < upper)]
        run.fitlc = run.fitlc[(lower < run.fitlc['date']) & (run.fitlc['date'] < upper)]
