"""
Code for plotting a caustic crossing path
"""
from typing import Union

import numpy as np
from pathlib import Path

from bokeh.models import Title
from bokeh.plotting import Figure

import moana
from moana.viewer.color_mapper import ColorMapper


class CausticCrossingViewer:
    @classmethod
    def figure_for_run_path(cls, run_path: Path, title: Union[None, str] = None) -> Figure:
        figure = Figure()
        if title is not None:
            title_ = Title()
            title_.text = title
            figure.title = title_
        fit_model = moana.dbc.io.Output(run_path.name, path=str(run_path.parent))
        fit_model.load()
        params = fit_model.param.to_dict()

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
        caustic_color = 'red'
        caustic_glpyh_radius = 0.01
        figure.diamond(x=real_component0, y=imaginary_component0, line_color=caustic_color, fill_alpha=0, size=2)

        # Lower part of the caustic (it is symmetric): 2nd half of the caustic
        real_component1 = np.real(half_caustic)
        imaginary_component1 = -np.imag(half_caustic)
        figure.diamond(x=real_component1, y=imaginary_component1, line_color=caustic_color, fill_alpha=0, size=2)

        # Plot the source trajectory
        x = fit_model.fitlc['xs']
        y = fit_model.fitlc['ys']
        color_mapper = ColorMapper()
        fit_color = color_mapper.get_fit_color(run_path.parent.stem[-20:])  # TODO: Don't do this here
        figure.line(x=x, y=y, color=fit_color, line_width=2)
        return figure
