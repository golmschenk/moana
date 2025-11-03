from typing import List

import numpy as np
import pandas as pd
import scipy.stats
from bokeh.models import Column, Row
from bokeh.plotting import Figure

from moana.david_bennett_fit.run import Run
from moana.viewer.color_mapper import ColorMapper


class GalacticModelViewer:
    @classmethod
    def comparison_for_runs(cls, runs: List[Run]) -> Column:
        rows = []
        for cumulative_distribution_data_path0 in runs[0].path.glob('*histI.dat'):
            color_mapper = ColorMapper()
            data_name = cumulative_distribution_data_path0.name.replace('mcmc_', '').replace('_histI.dat', '')
            is_log_scale = data_name in ['eps1', 'planetM', 'q']
            if is_log_scale:
                x_axis_type = 'log'
            else:
                x_axis_type = 'linear'

            cumulative_figure = Figure(x_axis_label=data_name, y_axis_label='Cumulative', x_axis_type=x_axis_type)
            density_figure = Figure(x_axis_label=data_name, y_axis_label='Density', x_range=cumulative_figure.x_range,
                                    x_axis_type=x_axis_type)

            for run in runs:
                run_color = color_mapper.get_fit_color(str(run.path))
                data_frame = pd.read_csv(run.path.joinpath(cumulative_distribution_data_path0.name), skiprows=2,
                                         delim_whitespace=True, header=None, index_col=None, skipinitialspace=True)
                run_cumulative_value_positions = data_frame[1]
                run_cumulative_sums = data_frame[0]
                cls.plot_distributions(cumulative_figure, density_figure, run_color, run_cumulative_sums,
                                       run_cumulative_value_positions, run.display_name, is_log_scale=is_log_scale)

            cumulative_figure.legend.location = "top_left"
            row = Row(cumulative_figure, density_figure)
            rows.append(row)

        column = Column(*rows)
        return column

    @classmethod
    def plot_distributions(cls, cumulative_figure, density_figure, color, cumulative_sums, cumulative_value_positions,
                           display_name, is_log_scale: bool = False):
        cumulative_figure.line(x=cumulative_value_positions, y=cumulative_sums, line_width=2,
                               color=color,
                               legend_label=display_name)
        densities, density_value_positions = cls.density_distribution_from_cumulative_distribution(
            cumulative_value_positions, is_log_scale=is_log_scale)
        density_figure.line(x=density_value_positions, y=densities, line_width=2, color=color,
                            legend_label=display_name)

    @staticmethod
    def density_distribution_from_cumulative_distribution(cumulative_value_positions: np.ndarray,
                                                          is_log_scale: bool = False) -> (np.ndarray, np.ndarray):
        if is_log_scale:
            cumulative_value_positions = np.log10(cumulative_value_positions)
        kernel = scipy.stats.gaussian_kde(cumulative_value_positions)
        minimum = np.min(cumulative_value_positions)
        maximum = np.max(cumulative_value_positions)
        difference = maximum - minimum
        plotting_positions = np.linspace(minimum - (difference * 0.1), maximum + (difference * 0.1), 500)
        densities = kernel(plotting_positions)
        if is_log_scale:
            plotting_positions = 10 ** plotting_positions
        return densities, plotting_positions

    @staticmethod
    def density_distribution_from_cumulative_distribution2(cumulative_value_positions: np.ndarray
                                                           ) -> (np.ndarray, np.ndarray):
        densities, density_edges = np.histogram(cumulative_value_positions, bins=30, density=True)
        density_midpoints = (density_edges[1:] + density_edges[:-1]) / 2
        return densities, density_midpoints

    @staticmethod
    def density_distribution_from_cumulative_distribution3(cumulative_value_positions: np.ndarray,
                                                           cumulative_sums: np.ndarray) -> (np.ndarray, np.ndarray):
        densities = np.gradient(cumulative_sums, cumulative_value_positions)
        density_value_positions = (cumulative_value_positions[1:] + cumulative_value_positions[:-1]) / 2
        return densities, density_value_positions
