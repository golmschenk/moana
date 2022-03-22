"""
Code for plotting a caustic crossing path
"""
import pickle
import sys
from pathlib import Path
from typing import Union

import numpy as np
from matplotlib import pyplot as plt, cm, ticker
from matplotlib.colors import LogNorm, SymLogNorm
from numpy import ma
from scipy import spatial

from bokeh.models import Title, PanTool, BoxZoomTool, WheelZoomTool, ResetTool
from bokeh.plotting import Figure
from bokeh.models import DataRange1d, Arrow, NormalHead

import moana
try:
    from main_resources.theme import paper_themed_figure_and_axes
except ModuleNotFoundError:  # TODO: Terrible hack. This should be redone.
    sys.path.insert(0, '/Users/golmschenk/Documents/2021_microlensing_event_moa_2020_blg_208_paper')
    from main_resources.theme import paper_themed_figure_and_axes
from moana.david_bennett_fit.names import NameEnum
from moana.david_bennett_fit.run import Run
from moana.viewer.color_mapper import ColorMapper
from bokeh import palettes


try:
    from luckylensing.luckylensing import rayshoot
    from luckylensing.luckylensing import lensconfig
except ImportError as import_error:
    def raise_error_on_use():
        raise import_error
    rayshoot = raise_error_on_use
    lensconfig = raise_error_on_use


class CausticCrossingViewer:
    @classmethod
    def figure_for_run(cls, run: Run, title: Union[None, str] = None) -> Figure:
        figure = Figure(match_aspect=True, tools=[PanTool(), BoxZoomTool(match_aspect=True),
                                                  WheelZoomTool(zoom_on_axis=False), ResetTool()])
        if title is not None:
            title_ = Title()
            title_.text = title
            figure.title = title_
        imaginary_component, real_component = extract_caustics(run)
        x_arithmetic_range = real_component.max() - real_component.min()
        y_arithmetic_range = imaginary_component.max() - imaginary_component.min()
        x_padding = (x_arithmetic_range) * 0.1
        y_padding = (y_arithmetic_range) * 0.1

        caustic_color = palettes.Category10[3][0]
        caustic_glpyh_radius = 0.01
        figure.diamond(x=real_component, y=imaginary_component, line_color=caustic_color,
                       fill_alpha=0, size=2)
        y_mean = imaginary_component.mean()
        x_mean = real_component.mean()

        # Plot the source trajectory
        trajectory_x, trajectory_y = get_run_source_trajectory(run)
        color_mapper = ColorMapper()
        fit_color = color_mapper.get_fit_color(str(run.path))
        figure.line(x=trajectory_x, y=trajectory_y, color=fit_color, line_width=2)


        # Create directional arrow.
        points_array = np.stack([trajectory_y, trajectory_x], axis=1)
        distance, closest_to_centroid_index = spatial.KDTree(points_array).query([y_mean, x_mean])
        figure.add_layout(Arrow(end=NormalHead(line_alpha=0.0, fill_color=fit_color),
                                line_alpha = 0.0,
                                x_start=trajectory_x[closest_to_centroid_index - int(len(trajectory_x) * 0.1)],
                                y_start=trajectory_y[closest_to_centroid_index - int(len(trajectory_x) * 0.1)],
                                x_end=trajectory_x[closest_to_centroid_index],
                                y_end=trajectory_y[closest_to_centroid_index]))


        if x_arithmetic_range > y_arithmetic_range:
            figure.x_range.start = real_component.min() - x_padding
            figure.x_range.end = real_component.max() + x_padding
            figure.y_range.start = y_mean - (x_arithmetic_range / 2)
            figure.y_range.end = y_mean + (x_arithmetic_range / 2)
        else:
            figure.x_range.start = x_mean - (y_arithmetic_range / 2)
            figure.x_range.end = x_mean + (y_arithmetic_range / 2)
            figure.y_range.start = imaginary_component.min() - y_padding
            figure.y_range.end = imaginary_component.max() + y_padding

        return figure

def extract_caustics(run):
    params = run.dbc_output.param.to_dict()
    # Create a MOANA lens object (ignore the name 'ResonantCaustic'), it works for all caustics.
    lens = moana.lens.ResonantCaustic(**params)
    # Compute the center of mass location
    params.update({'gl1': moana.lens.Microlens(**params)._gl1})
    # Compute the caustic shape. Choose the sampling you need to have a nice continuous caustic
    N = 400
    lens._sample(N)
    # Change reference frame to convention of Dave's code
    frame_dave = moana.LensReferenceFrame(center='barycenter', x_axis='21')
    frame_cas = moana.LensReferenceFrame(center='primary', x_axis='21')
    half_caustic = frame_cas.to_frame(lens.full['zeta'].values, frame_dave, **params)
    # Upper part of the caustic (first half of the caustic)
    real_component0 = np.real(half_caustic)
    imaginary_component0 = np.imag(half_caustic)
    # Lower part of the caustic (it is symmetric): 2nd half of the caustic
    real_component1 = np.real(half_caustic)
    imaginary_component1 = -np.imag(half_caustic)
    real_component = np.concatenate([real_component0, real_component1])
    imaginary_component = np.concatenate([imaginary_component0, imaginary_component1])
    return imaginary_component, real_component

def get_run_source_trajectory(run):
    trajectory_x = run.dbc_output.fitlc['xs']
    trajectory_y = run.dbc_output.fitlc['ys']
    return trajectory_x, trajectory_y


def create_magnification_pattern_and_trajectory_figure(run):
    # Map of PSPL model
    number_of_x_pixels = 16384
    number_of_y_pixels = number_of_x_pixels

    imaginary_component, real_component = extract_caustics(run)
    trajectory_x, trajectory_y = get_run_source_trajectory(run)

    y_mean = imaginary_component.mean()
    x_mean = real_component.mean()
    x_arithmetic_range = real_component.max() - real_component.min()
    y_arithmetic_range = imaginary_component.max() - imaginary_component.min()
    x_padding = (x_arithmetic_range) * 0.1
    y_padding = (y_arithmetic_range) * 0.1

    if x_arithmetic_range > y_arithmetic_range:
        x_start = real_component.min() - x_padding
        x_end = real_component.max() + x_padding
        y_start = y_mean - (x_arithmetic_range / 2)
        y_end = y_mean + (x_arithmetic_range / 2)
    else:
        x_start = x_mean - (y_arithmetic_range / 2)
        x_end = x_mean + (y_arithmetic_range / 2)
        y_start = imaginary_component.min() - y_padding
        y_end = imaginary_component.max() + y_padding

    single_lens_parameters = [(0, 0, 1.0)]
    full_plotting_region = (x_start, y_start, x_end, y_end)
    ray_shooting_number_of_threads = 16
    recalc = True
    if recalc:
        single_lens_magnification_pattern = rayshoot(single_lens_parameters, full_plotting_region, number_of_x_pixels,
                                                     number_of_y_pixels, num_threads=ray_shooting_number_of_threads,
                                                     kernel='triangulated')
        with open('single_lens_magnification_pattern.pkl', 'wb') as handle:
            pickle.dump(single_lens_magnification_pattern, handle)
    else:
        with open('single_lens_magnification_pattern.pkl', 'rb') as handle:
            single_lens_magnification_pattern = pickle.load(handle)

    # Map of PSBL model
    lens_model_parameters = run.extract_final_parameters_from_run_output_file()
    sep = -lens_model_parameters[NameEnum.SECONDARY_SEPARATION].value
    q = moana.dbc.mass_fration_to_mass_ratio(lens_model_parameters[NameEnum.SECONDARY_EPSILON].value)
    binary_lens = lensconfig.binary_lenses(sep, q)
    if recalc:
        magnification_pattern_l2 = rayshoot(binary_lens, full_plotting_region, number_of_x_pixels, number_of_y_pixels,
                                            num_threads=ray_shooting_number_of_threads,
                                            kernel='triangulated')
        with open('magnification_pattern_l2.pkl', 'wb') as handle:
            pickle.dump(magnification_pattern_l2, handle)
    else:
        with open('magnification_pattern_l2.pkl', 'rb') as handle:
            magnification_pattern_l2 = pickle.load(handle)

    # # Map of the central caustic
    # central_region = (-0.012, -0.004, 0.004, 0.004)
    # number_of_x_pixels = 4 * 1024
    # number_of_y_pixels = 4 * 512
    # central_magnification_pattern = rayshoot(binary_lens, central_region, number_of_x_pixels, number_of_y_pixels,
    #                                          num_threads=4)
    #
    # figure, axes = plt.subplots()
    # image = axes.imshow(central_magnification_pattern, cmap="hot", origin='lower',
    #            norm=LogNorm(vmin=np.min(central_magnification_pattern), vmax=np.max(central_magnification_pattern)),
    #            extent=[central_region[0], central_region[2], central_region[1], central_region[3]])
    # figure.colorbar(image)
    # plt.show()

    magnification_difference = magnification_pattern_l2 - single_lens_magnification_pattern

    masked_magnification_difference = ma.masked_where(
        (magnification_difference < -0.2) | (magnification_difference > 0.2), magnification_difference)
    masked_magnification_difference.fill_value = 0

    # figure, axes = plt.subplots()
    # image = axes.imshow(masked_magnification_difference, cmap="coolwarm", origin='lower',
    #            extent=[full_plotting_region[0], full_plotting_region[2], full_plotting_region[1],
    #                    full_plotting_region[3]])
    #
    # figure.colorbar(image)
    # plt.show()


    for linear_threshold in [0.01]:
        with paper_themed_figure_and_axes() as (figure, axes):
            image = axes.imshow(magnification_difference, cmap=cm.get_cmap("coolwarm", 1000), origin='lower',
                                norm=SymLogNorm(linthresh=linear_threshold, vmin=np.min(magnification_difference),
                                                vmax=np.max(magnification_difference)),
                                extent=[full_plotting_region[0], full_plotting_region[2], full_plotting_region[1],
                                        full_plotting_region[3]])
            color_bar = figure.colorbar(image, location='top', shrink=0.6)
            color_bar.set_label('Magnification residual $A_{PSBL}-A_{PSPL}$')
            color_bar.set_ticks([-1e2, -1e-1, 0, 1e-1, 1e2])
            # color_bar.ax.set_xticklabels(color_bar.ax.get_xticklabels(), rotation=45)
            color_bar.ax.tick_params(rotation=45)
            axes.scatter(x=real_component, y=imaginary_component, c='white', s=0.2, linewidths=0)
            axes.plot(trajectory_x, trajectory_y, color='black', linewidth=1)
            points_array = np.stack([trajectory_y, trajectory_x], axis=1)
            distance, closest_to_centroid_index = spatial.KDTree(points_array).query([y_mean, x_mean])
            arrow_start_x = trajectory_x[closest_to_centroid_index - int(len(trajectory_x) * 0.1)]
            arrow_start_y = trajectory_y[closest_to_centroid_index - int(len(trajectory_x) * 0.1)]
            arrow_end_x = trajectory_x[closest_to_centroid_index]
            arrow_end_y = trajectory_y[closest_to_centroid_index]
            axes.arrow(arrow_start_x,
                       arrow_start_y,
                       arrow_end_x - arrow_start_x,
                       arrow_end_y - arrow_start_y,
                       shape='full', lw=0, length_includes_head=True, head_width=.015, facecolor='black')
            axes.set_xlim(x_start, x_end)
            axes.set_ylim(y_start, y_end)
            axes.set_xlabel(r'$\theta_{x} / \theta_{E}$')
            axes.set_ylabel(r'$\theta_{y} / \theta_{E}$')
            # figure.tight_layout()
            # plt.subplots_adjust(left=-0.1, right=1.1, top=0.8, bottom=0.15)
            # plt.show()
            plt.savefig('magnification_pattern.png', transparent=True, dpi=500)
    # figure, axes = plt.subplots()
    # image = axes.imshow(magnification_pattern_l2, cmap="hot", origin='lower',
    #            norm=LogNorm(vmin=np.min(magnification_pattern_l2), vmax=np.max(magnification_pattern_l2)),
    #            extent=[full_plotting_region[0], full_plotting_region[2], full_plotting_region[1], full_plotting_region[3]])
    # figure.colorbar(image)
    # plt.show()



def find_index_of_xy_closest_to_point(y_array: np.ndarray, x_array: np.ndarray, y_point: float, x_point: float):
    distance = (y_array - y_point) ** 2 + (x_array - x_point) ** 2
    idy, idx = np.where(distance == distance.min())
    return idy[0], idx[0]


if __name__ == '__main__':
    run_ = Run(Path('/Users/golmschenk/Code/moana/data/mb20208/runs/clean_slate_wide_only_moa_initial_mcmc_step1_2022_03_17_dl_2022_03_22'))
    create_magnification_pattern_and_trajectory_figure(run_)
