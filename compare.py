from pathlib import Path
from bokeh.io import show
from bokeh.models import Row, Column
from moana import dbc
from moana.viewer.caustic_crossing_viewer import CausticCrossingViewer
from moana.viewer.caustic_topology_viewer import CausticTopologyViewer
from moana.viewer.delta_chi_squared_viewer import ChiSquaredViewer

from moana.viewer.run_modifier import RunModifier
from moana.viewer.run_fit_viewer import RunFitViewer

run_path1 = Path('data/mb20208/runs/MOA only runs that actually finished (old style)/close_detailed_moa_mcmc0_cont_2021-02-04-11-21-55')
run_path0 = Path('data/mb20208/runs/MOA only runs that actually finished (old style)/wide_detailed_moa_parallax_mcmc0_cont_2021-02-04-11-21-55')

run0 = dbc.Output('run_1', path=run_path0)
run0.load()
run1 = dbc.Output('run_1', path=run_path1)
run1.load()

run_modifier = RunModifier()
run_modifier.limit_date_range(run0, 9075, 9125)
run_modifier.limit_date_range(run1, 9075, 9125)

viewer = RunFitViewer()
parameter_comparison_table = viewer.create_run_parameter_comparison_table(run_path0, run_path1)
left_comparison_view = viewer.create_comparison_view(run0, run1)
right_comparison_view = viewer.create_comparison_view(run0, run1)

side_by_side_clone_comparison_view = Row(left_comparison_view, right_comparison_view)
side_by_side_clone_comparison_view.sizing_mode = 'stretch_width'

caustic_topology_figure = CausticTopologyViewer.figure_for_multiple_run_paths([run_path0, run_path1])
caustic_crossing_figure0 = CausticCrossingViewer.figure_for_run_path(run_path0)
caustic_crossing_figure1 = CausticCrossingViewer.figure_for_run_path(run_path1)
caustic_figures = [caustic_topology_figure, caustic_crossing_figure0, caustic_crossing_figure1]
for figure in caustic_figures:
    figure.sizing_mode = 'stretch_width'
caustic_row = Row(*caustic_figures)
caustic_row.sizing_mode = 'stretch_width'

bottom_parameter_comparison_table = viewer.create_run_parameter_comparison_table(run_path0, run_path1)

cumulative_delta_chi_squared_figure = ChiSquaredViewer.for_comparison_of_two_fit_models(run_path0, run_path1)
cumulative_delta_chi_squared_figure.sizing_mode = 'stretch_width'

column = Column(parameter_comparison_table, side_by_side_clone_comparison_view, caustic_row,
                bottom_parameter_comparison_table, cumulative_delta_chi_squared_figure)
column.sizing_mode = 'stretch_width'
show(column)
