from pathlib import Path
from bokeh.io import show
from bokeh.models import Row, Column
from moana.david_bennett_fit.run import Run
from moana.viewer.caustic_crossing_viewer import CausticCrossingViewer
from moana.viewer.caustic_topology_viewer import CausticTopologyViewer
from moana.viewer.delta_chi_squared_viewer import ChiSquaredViewer
from moana.viewer.galatic_model_viewer import GalacticModelViewer

from moana.viewer.run_modifier import RunModifier
from moana.viewer.run_fit_viewer import RunFitViewer

run1 = Run(Path('data/mb20208/runs/close_detailed_moa_parallax_mcmc1_continue0_calc_2021-03-11-18-50-48'))
run0 = Run(Path('data/mb20208/runs/wide_detailed_moa_parallax_mcmc1_continue0_calc_2021-03-11-18-50-48'))
Run.make_short_display_names_from_unique_directory_name_components([run0, run1])

run_modifier = RunModifier()
run_modifier.limit_date_range(run0.dbc_output, 9075, 9125)
run_modifier.limit_date_range(run1.dbc_output, 9075, 9125)

viewer = RunFitViewer()
parameter_comparison_table = viewer.create_run_parameter_comparison_table(run0, run1)
left_comparison_view = viewer.create_comparison_view(run0, run1)
right_comparison_view = viewer.create_comparison_view(run0, run1)

side_by_side_clone_comparison_view = Row(left_comparison_view, right_comparison_view)
side_by_side_clone_comparison_view.sizing_mode = 'stretch_width'

caustic_topology_figure = CausticTopologyViewer.figure_for_multiple_runs([run0, run1])
caustic_crossing_figure0 = CausticCrossingViewer.figure_for_run_path(run0)
caustic_crossing_figure1 = CausticCrossingViewer.figure_for_run_path(run1)
caustic_figures = [caustic_topology_figure, caustic_crossing_figure0, caustic_crossing_figure1]
for figure in caustic_figures:
    figure.sizing_mode = 'stretch_width'
caustic_row = Row(*caustic_figures)
caustic_row.sizing_mode = 'stretch_width'

bottom_parameter_comparison_table = viewer.create_run_parameter_comparison_table(run0, run1)

cumulative_delta_chi_squared_figure = ChiSquaredViewer.for_comparison_of_two_fit_models(run0, run1)
cumulative_delta_chi_squared_figure.sizing_mode = 'stretch_width'

galactic_model_cumulative_distributions = GalacticModelViewer.comparison_for_runs(run0, run1)

column = Column(parameter_comparison_table, side_by_side_clone_comparison_view, caustic_row,
                bottom_parameter_comparison_table, cumulative_delta_chi_squared_figure,
                galactic_model_cumulative_distributions)
column.sizing_mode = 'stretch_width'
show(column)
