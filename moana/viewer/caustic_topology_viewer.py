"""
Code for displaying the caustic topology.
"""
from typing import List
import numpy as np
from pathlib import Path
from bokeh.plotting import Figure

import moana
from moana.viewer.color_mapper import ColorMapper


class CausticTopologyViewer:
    @classmethod
    def figure_for_run_path(cls, run_path: Path) -> Figure:
        viewer = CausticTopologyViewer()
        figure = viewer.create_caustic_topology_figure()
        viewer.add_run_to_figure(figure, run_path)
        return figure

    @classmethod
    def figure_for_multiple_run_paths(cls, run_paths: List[Path]) -> Figure:
        viewer = CausticTopologyViewer()
        figure = viewer.create_caustic_topology_figure()
        for run_path in run_paths:
            viewer.add_run_to_figure(figure, run_path)
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
    def add_run_to_figure(figure: Figure, run_path: Path):
        fit_model = moana.dbc.io.Output('run_1', path=str(run_path))
        fit_model.load()
        fit_model.run = run_path.stem[-20:]  # TODO: Don't do this here.
        color_mapper = ColorMapper()
        color = color_mapper.get_fit_color(fit_model.run)
        figure.circle(x=fit_model.param['sep'], y=fit_model.param['q'], size=20, alpha=0.5, color=color)
