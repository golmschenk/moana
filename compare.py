from pathlib import Path

import numpy as np
import pandas as pd
from bokeh.io import show, save
from bokeh.models import Row, Column

from main_resources.run_paths import wide_model_run_path, close_model_run_path, single_source_single_lens_run_path, \
    second_wide_model_run_path, second_close_model_run_path
from moana.david_bennett_fit.names import BinarySourceModelParameterNameEnum
from moana.david_bennett_fit.run import Run
from moana.light_curve import LightCurve, ColumnName
from moana.viewer.caustic_crossing_viewer import CausticCrossingViewer
from moana.viewer.caustic_topology_viewer import CausticTypeBoundaryViewer
from moana.viewer.delta_chi_squared_viewer import ChiSquaredViewer
from moana.viewer.galatic_model_viewer import GalacticModelViewer

from moana.viewer.run_modifier import RunModifier
from moana.viewer.run_fit_viewer import RunFitViewer

np.seterr(all='raise')

run0 = Run(wide_model_run_path)
run1 = Run(close_model_run_path)
# Run.make_short_display_names_from_unique_directory_name_components([run0, run1])
run0.dbc_output.load()
run1.dbc_output.load()
# moana_data_frame = run0.dbc_output.resid
# microlensing_hjd = moana_data_frame['date']
# magnification = moana_data_frame['mgf_data']
# magnification_error = moana_data_frame['sig_mgf']
# magnification_residual = moana_data_frame['res_mgf']
# light_curve_data_frame = pd.DataFrame({ColumnName.TIME__MICROLENSING_HJD.value: microlensing_hjd,
#                                        'magnification': magnification,
#                                        'magnification_error': abs(magnification_error),
#                                        'instrument_identifier': moana_data_frame['sfx']})
# from astropy.table import Table
# from astropy.io import ascii
# table: Table = Table.from_pandas(light_curve_data_frame)
# ascii.write(table, 'figure1_light_curve.mrt', format='mrt', overwrite=True)

run_modifier = RunModifier()
run_modifier.limit_date_range(run0.dbc_output, 9075, 9125)
run_modifier.limit_date_range(run1.dbc_output, 9075, 9125)
# run_modifier.remove_instrument_suffix(run0, 'moa2v')
# run_modifier.remove_instrument_suffix(run1, 'moa2v')
# for run in [run0, run1]:
#     run_modifier.filter_instrument_suffixes_to_keep(run, ['moa2v', 'moa2r', 'kmtA22', 'lco1'])

viewer = RunFitViewer()
parameter_comparison_table = viewer.create_run_parameter_comparison_table(
    run0, run1)
left_comparison_view = viewer.create_light_curve_with_residuals_view(run0)
right_comparison_view = viewer.create_light_curve_with_residuals_view(run1)

side_by_side_clone_comparison_view = Row(left_comparison_view, right_comparison_view)
side_by_side_clone_comparison_view.sizing_mode = 'stretch_width'

caustic_topology_figure = CausticTypeBoundaryViewer.figure_for_multiple_runs([run0, run1])
caustic_crossing_figure0 = CausticCrossingViewer.figure_for_run(run0)
caustic_crossing_figure1 = CausticCrossingViewer.figure_for_run(run1)
caustic_figures = [caustic_topology_figure, caustic_crossing_figure0, caustic_crossing_figure1]
for figure in caustic_figures:
    figure.sizing_mode = 'stretch_width'
caustic_row = Row(*caustic_figures)
caustic_row.sizing_mode = 'stretch_width'


bottom_parameter_comparison_table = viewer.create_run_parameter_comparison_table(
    run0, run1)
cumulative_delta_chi_squared_figure = ChiSquaredViewer.for_comparison_of_two_fit_models_per_instrument(run0, run1)
cumulative_delta_chi_squared_figure.sizing_mode = 'stretch_width'

# galactic_model_cumulative_distributions = GalacticModelViewer.comparison_for_runs([run0, run1])

column = Column(parameter_comparison_table,
                side_by_side_clone_comparison_view,
                caustic_row,
                bottom_parameter_comparison_table,
                cumulative_delta_chi_squared_figure,
                # galactic_model_cumulative_distributions
                )
column.sizing_mode = 'stretch_width'
show(column)
save(column, 'compare.html')
pass
