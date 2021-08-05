"""
Code for plotting a caustic crossing path
"""
from typing import Union

import numpy as np

from bokeh.models import Title, PanTool, BoxZoomTool, WheelZoomTool, ResetTool
from bokeh.plotting import Figure
from bokeh.models import DataRange1d

import moana
from moana.david_bennett_fit.run import Run
from moana.viewer.color_mapper import ColorMapper


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
        caustic_color = 'red'
        caustic_glpyh_radius = 0.01
        figure.diamond(x=real_component, y=imaginary_component, line_color=caustic_color,
                       fill_alpha=0, size=2)

        # Plot the source trajectory
        x = run.dbc_output.fitlc['xs']
        y = run.dbc_output.fitlc['ys']
        color_mapper = ColorMapper()
        fit_color = color_mapper.get_fit_color(str(run.path))
        figure.line(x=x, y=y, color=fit_color, line_width=2)

        x_arithmetic_range = real_component.max() - real_component.min()
        y_arithmetic_range = imaginary_component.max() - imaginary_component.min()
        x_padding = (x_arithmetic_range) * 0.1
        y_padding = (y_arithmetic_range) * 0.1

        if x_arithmetic_range > y_arithmetic_range:
            figure.x_range.start = real_component.min() - x_padding
            figure.x_range.end = real_component.max() + x_padding
            figure.y_range.start = imaginary_component.mean() - (x_arithmetic_range / 2)
            figure.y_range.end = imaginary_component.mean() + (x_arithmetic_range / 2)
        else:
            figure.x_range.start = real_component.mean() - (y_arithmetic_range / 2)
            figure.x_range.end = real_component.mean() + (y_arithmetic_range / 2)
            figure.y_range.start = imaginary_component.min() - y_padding
            figure.y_range.end = imaginary_component.max() + y_padding

        return figure
