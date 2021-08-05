"""
Code for plotting a caustic crossing path
"""
from typing import Union

import numpy as np
from scipy import spatial

from bokeh.models import Title, PanTool, BoxZoomTool, WheelZoomTool, ResetTool
from bokeh.plotting import Figure
from bokeh.models import DataRange1d, Arrow, NormalHead

import moana
from moana.david_bennett_fit.run import Run
from moana.viewer.color_mapper import ColorMapper
from bokeh import palettes


class CausticCrossingViewer:
    @classmethod
    def figure_for_run(cls, run: Run, title: Union[None, str] = None) -> Figure:
        figure = Figure(match_aspect=True, tools=[PanTool(), BoxZoomTool(match_aspect=True),
                                                  WheelZoomTool(zoom_on_axis=False), ResetTool()])
        if title is not None:
            title_ = Title()
            title_.text = title
            figure.title = title_
        params = run.dbc_output.param.to_dict()

        # Create a MOANA lens object (do not care about the name 'ResonantCaustic'),
        # it works for all caustics.
        lens = moana.lens.ResonantCaustic(**params)

        # Compute the center of mass location
        params.update({'gl1': moana.lens.Microlens(**params)._gl1})

        # Compute the caustic shape. Choose the sampling you need to have a nice
        # continuous caustic
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
        caustic_color = palettes.Category10[3][0]
        caustic_glpyh_radius = 0.01
        figure.diamond(x=real_component, y=imaginary_component, line_color=caustic_color,
                       fill_alpha=0, size=2)

        # Plot the source trajectory
        trajectory_x = run.dbc_output.fitlc['xs']
        trajectory_y = run.dbc_output.fitlc['ys']
        color_mapper = ColorMapper()
        fit_color = color_mapper.get_fit_color(str(run.path))
        figure.line(x=trajectory_x, y=trajectory_y, color=fit_color, line_width=2)

        x_arithmetic_range = real_component.max() - real_component.min()
        y_arithmetic_range = imaginary_component.max() - imaginary_component.min()
        y_mean = imaginary_component.mean()
        x_mean = real_component.mean()

        # Create directional arrow.
        points_array = np.stack([trajectory_y, trajectory_x], axis=1)
        distance, closest_to_centroid_index = spatial.KDTree(points_array).query([y_mean, x_mean])
        figure.add_layout(Arrow(end=NormalHead(line_alpha=0.0, fill_color=fit_color),
                                line_alpha = 0.0,
                                x_start=trajectory_x[closest_to_centroid_index - int(len(trajectory_x) * 0.1)],
                                y_start=trajectory_y[closest_to_centroid_index - int(len(trajectory_x) * 0.1)],
                                x_end=trajectory_x[closest_to_centroid_index],
                                y_end=trajectory_y[closest_to_centroid_index]))

        x_padding = (x_arithmetic_range) * 0.1
        y_padding = (y_arithmetic_range) * 0.1

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


def find_index_of_xy_closest_to_point(y_array: np.ndarray, x_array: np.ndarray, y_point: float, x_point: float):
    distance = (y_array - y_point) ** 2 + (x_array - x_point) ** 2
    idy, idx = np.where(distance == distance.min())
    return idy[0], idx[0]
