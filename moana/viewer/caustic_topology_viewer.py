"""
Code for displaying the caustic topology.
"""
from typing import List
import numpy as np
from bokeh.plotting import Figure

import moana
from moana.david_bennett_fit.run import Run
from moana.viewer.color_mapper import ColorMapper


class CausticTopologyViewer:
    @classmethod
    def figure_for_run_path(cls, run: Run) -> Figure:
        viewer = CausticTopologyViewer()
        figure = viewer.create_caustic_topology_figure()
        viewer.add_run_to_figure(figure, run)
        return figure

    @classmethod
    def figure_for_multiple_runs(cls, runs: List[Run]) -> Figure:
        viewer = CausticTopologyViewer()
        figure = viewer.create_caustic_topology_figure()
        for run in runs:
            viewer.add_run_to_figure(figure, run)
        return figure

    @staticmethod
    def create_caustic_topology_figure():
        figure = Figure(x_axis_label='Separation', y_axis_label='Mass ratio', x_axis_type='log', y_axis_type='log')
        mass_ratios = np.logspace(-5, 0, 100)
        wide_to_resonant_caustic_limit_separations = moana.lens.wide_limit_2l(mass_ratios)
        close_to_resonant_caustic_limit_separations = moana.lens.close_limit_2l(mass_ratios)
        limit_line_color = 'black'
        figure.line(x=close_to_resonant_caustic_limit_separations, y=mass_ratios, line_color=limit_line_color,
                    line_width=2)
        figure.line(x=wide_to_resonant_caustic_limit_separations, y=mass_ratios, line_color=limit_line_color,
                    line_width=2)
        return figure

    @staticmethod
    def add_run_to_figure(figure: Figure, run: Run):
        color_mapper = ColorMapper()
        color = color_mapper.get_fit_color(str(run.path))
        figure.circle(x=run.dbc_output.param['sep'], y=run.dbc_output.param['q'], size=20, alpha=0.5, color=color)
