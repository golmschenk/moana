"""
Code for displaying the caustic topology.
"""
import numpy as np
from pathlib import Path
from bokeh.plotting import Figure

import moana
from moana.dbc import Output


class CausticTopologyViewer:
    @classmethod
    def figure_for_run(cls, run_path: Path) -> Figure:
        viewer = CausticTopologyViewer()
        figure = Figure(x_axis_label='Separation', y_axis_label='Mass ratio')
        mass_ratios = np.logspace(-5, 0, 100)
        wide_to_resonant_caustic_limit_separations = moana.lens.wide_limit_2l(mass_ratios)
        close_to_resonant_caustic_limit_separations = moana.lens.close_limit_2l(mass_ratios)
        limit_line_color = 'black'
        figure.line(x=close_to_resonant_caustic_limit_separations, y=mass_ratios, line_color=limit_line_color,
                    line_width=2)
        figure.line(x=wide_to_resonant_caustic_limit_separations, y=mass_ratios, line_color=limit_line_color,
                    line_width=2)
        viewer.add_run_to_figure(figure, run_path)
        return figure

    @staticmethod
    def add_run_to_figure(figure: Figure, run_path: Path):
        fit_model = moana.dbc.io.Output(run_path.name, path=str(run_path.parent))
        fit_model.load()
        figure.circle(x=fit_model.param['sep'], y=fit_model.param['q'], size=20, alpha=0.5)
