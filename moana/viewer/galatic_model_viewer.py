import numpy as np
import pandas as pd
import scipy.stats
from bokeh.models import Column, Row
from bokeh.plotting import Figure

from moana.david_bennett_fit.run import Run
from moana.viewer.color_mapper import ColorMapper


class GalacticModelViewer:
    @classmethod
    def comparison_for_runs(cls, run0: Run, run1: Run) -> Column:
        rows = []
        for cumulative_distribution_data_path0 in run0.path.glob('*histI.dat'):
            color_mapper = ColorMapper()
            run0_color = color_mapper.get_fit_color(str(run0.path))
            run1_color = color_mapper.get_fit_color(str(run1.path))

            data_frame0 = pd.read_csv(cumulative_distribution_data_path0, skiprows=2, delim_whitespace=True, header=None, index_col=None, skipinitialspace=True)
            data_frame1 = pd.read_csv(run1.path.joinpath(cumulative_distribution_data_path0.name), skiprows=2, delim_whitespace=True, header=None, index_col=None, skipinitialspace=True)
            data_name = cumulative_distribution_data_path0.name.replace('mcmc_', '').replace('_histI.dat', '')
            cumulative_figure = Figure(x_axis_label=data_name, y_axis_label='Cumulative')
            density_figure = Figure(x_axis_label=data_name, y_axis_label='Density', x_range=cumulative_figure.x_range)
            run0_cumulative_value_positions = data_frame0[1]
            run0_cumulative_sums = data_frame0[0]
            cls.plot_distributions(cumulative_figure, density_figure, run0_color, run0_cumulative_sums,
                                   run0_cumulative_value_positions, run0.display_name)
            run1_cumulative_value_positions = data_frame1[1]
            run1_cumulative_sums = data_frame1[0]
            cls.plot_distributions(cumulative_figure, density_figure, run1_color, run1_cumulative_sums,
                                   run1_cumulative_value_positions, run1.display_name)
            cumulative_figure.legend.location = "top_left"
            row = Row(cumulative_figure, density_figure)
            rows.append(row)

        column = Column(*rows)
        return column

    @classmethod
    def plot_distributions(cls, cumulative_figure, density_figure, color, cumulative_sums, cumulative_value_positions,
                           display_name):
        cumulative_figure.line(x=cumulative_value_positions, y=cumulative_sums, line_width=2,
                               color=color,
                               legend_label=display_name)
        densities, density_value_positions = cls.density_distribution_from_cumulative_distribution(
            cumulative_value_positions)
        density_figure.line(x=density_value_positions, y=densities, line_width=2, color=color,
                            legend_label=display_name)

    @staticmethod
    def density_distribution_from_cumulative_distribution(cumulative_value_positions: np.ndarray
                                                          ) -> (np.ndarray, np.ndarray):
        kernel = scipy.stats.gaussian_kde(cumulative_value_positions)
        plotting_positions = np.linspace(np.min(cumulative_value_positions), np.max(cumulative_value_positions), 500)
        densities = kernel(plotting_positions)
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
