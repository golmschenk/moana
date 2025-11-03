import pandas as pd
from bokeh.colors import Color
from bokeh.models import ColumnDataSource, Whisker
from bokeh.plotting import Figure

from moana.light_curve import LightCurve, ColumnName, FitModelColumnName
from moana.viewer.color_mapper import ColorMapper


class LightCurveViewer:
    @classmethod
    def create_figure_for_light_curve(cls, light_curve: LightCurve) -> Figure:
        light_curve_figure = Figure()
        light_curve_figure.sizing_mode = 'stretch_width'

        color_mapper = ColorMapper()
        instrument_color = color_mapper.get_instrument_color(light_curve.instrument_suffix)
        cls.add_light_curve_points_with_errors_to_figure(
            light_curve_figure, light_curve.data_frame, light_curve.instrument_suffix, instrument_color,
            y_column_name=ColumnName.PHOTOMETRIC_MEASUREMENT.value,
            y_column_error_name=ColumnName.PHOTOMETRIC_MEASUREMENT_ERROR.value)

        return light_curve_figure

    @staticmethod
    def add_light_curve_points_with_errors_to_figure(figure: Figure, light_curve_data_frame: pd.DataFrame, name: str,
                                                     color: Color, y_column_name=FitModelColumnName.MAGNIFICATION.value,
                                                     y_column_error_name=FitModelColumnName.MAGNIFICATION_ERROR.value):
        light_curve_data_frame = light_curve_data_frame.copy()
        light_curve_data_frame['plus_error'] = light_curve_data_frame[y_column_name
                                               ] + light_curve_data_frame[y_column_error_name]
        light_curve_data_frame['minus_error'] = light_curve_data_frame[y_column_name
                                                ] - light_curve_data_frame[y_column_error_name]
        source = ColumnDataSource(light_curve_data_frame)
        line_alpha = 0.8
        fill_alpha = 0.2
        circle_renderer = figure.circle(source=source, x=ColumnName.TIME__MICROLENSING_HJD.value,
                                        y=y_column_name, legend_label=name,
                                        color=color, line_alpha=line_alpha, fill_alpha=fill_alpha)
        whisker = Whisker(source=source, base=ColumnName.TIME__MICROLENSING_HJD.value, upper='plus_error',
                          lower='minus_error', line_alpha=line_alpha,
                          line_color=circle_renderer.glyph.fill_color)
        whisker.upper_head.line_color = circle_renderer.glyph.fill_color
        whisker.upper_head.line_alpha = line_alpha
        whisker.lower_head.line_color = circle_renderer.glyph.fill_color
        whisker.lower_head.line_alpha = line_alpha
        figure.add_layout(whisker)
