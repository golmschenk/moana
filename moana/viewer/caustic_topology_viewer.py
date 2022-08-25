"""
Code for displaying the caustic topology.
"""
from typing import List, Optional
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
    def figure_for_multiple_runs(cls, runs: List[Run], legend_labels: Optional[List[str]] = None) -> Figure:
        viewer = CausticTopologyViewer()
        figure = viewer.create_caustic_topology_figure()
        for index, run in enumerate(runs):
            legend_label = None
            if legend_labels is not None:
                legend_label = legend_labels[index]
            viewer.add_run_to_figure(figure, run, legend_label, dot=bool(index))
        return figure

    @staticmethod
    def create_caustic_topology_figure():
        figure = Figure(x_axis_label='Separation', y_axis_label='Mass ratio', y_axis_type='log')
        mass_ratios = np.logspace(-5, -0.01, 100)
        wide_to_resonant_caustic_limit_separations = moana.lens.wide_limit_2l(mass_ratios)
        close_to_resonant_caustic_limit_separations = moana.lens.close_limit_2l(mass_ratios)
        limit_line_color = 'black'
        figure.line(x=close_to_resonant_caustic_limit_separations, y=mass_ratios, line_color=limit_line_color,
                    line_width=2)
        figure.line(x=wide_to_resonant_caustic_limit_separations, y=mass_ratios, line_color=limit_line_color,
                    line_width=2)
        figure.x_range.start = 0.3
        figure.x_range.end = 2.3
        figure.y_range.start = mass_ratios.min()
        figure.y_range.end = mass_ratios.max()
        return figure

    @staticmethod
    def add_run_to_figure(figure: Figure, run: Run, legend_label: Optional[str] = None, dot: bool = False):
        color_mapper = ColorMapper()
        color = color_mapper.get_fit_color(str(run.path))
        kwargs = {}
        if legend_label is not None:
            kwargs['legend_label'] = legend_label
        if dot:
            figure.circle_dot(x=run.dbc_output.param['sep'], y=run.dbc_output.param['q'], size=20, alpha=0.5,
                              color=color, **kwargs)
        else:
            figure.circle(x=run.dbc_output.param['sep'], y=run.dbc_output.param['q'], size=20, alpha=0.5, color=color,
                          **kwargs)
