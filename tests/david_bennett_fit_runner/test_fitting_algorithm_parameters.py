import re
from pathlib import Path
from unittest.mock import Mock, patch

from moana.david_bennett_fit.fitting_algorithm_parameters import FittingAlgorithmParameters


# noinspection SpellCheckingInspection
fake_david_bennett_parameter_file_content_lines = [
    "# daycausmin   daycausmax   deltcaus  delfine   gridUstar   hcut   iend    grid_rat\n",
    "  9075.0       9125.0         0.002    0.002     0.01       0.15    2      1.00\n",
    "# jclr  fudge  errmin  fmin    fmax    ald      bld      dayoff     sfx\n",
    "   0    1.0    0.014   0.01    1.10   0.6310   0.0000      0.000   'op'\n",
    "   1    1.0    0.014   0.01    1.10   0.7730   0.0000      0.000   'op'\n"
]


class TestFittingAlgorithmParameters:
    def test_can_load_parameters_list_from_david_bennett_parameter_file(self):
        with patch.object(Path, 'open') as stub_open:
            stub_read_lines = Mock(return_value=fake_david_bennett_parameter_file_content_lines)
            stub_open.return_value.__enter__.return_value = Mock(readlines=stub_read_lines)
            path = Path('')
            fitting_algorithm_parameters = FittingAlgorithmParameters.from_david_bennett_parameter_file_path(path)
            assert fitting_algorithm_parameters.detailed_time_step_start == 9075.0
            assert fitting_algorithm_parameters.h_cut == 0.15

    def test_can_create_david_bennett_input_string_from_parameters_dictionary(self):
        fitting_algorithm_parameters = FittingAlgorithmParameters(
            detailed_time_step_start=9075.0,
            detailed_time_step_end=9125.0,
            delt_caus=0.002,
            del_fine=0.002,
            integration_grid_radial_step_size=0.01,
            h_cut=0.15,
            i_end=2,
            integration_grid_radial_to_angular_ratio=1.0
        )
        parameter_file_string = fitting_algorithm_parameters.to_david_bennett_parameter_file_string()
        assert re.search(r"#\s+daycausmin\s+daycausmax\s+deltcaus\s+delfine\s+gridUstar\s+hcut\s+iend\s+grid_rat\n",
                         parameter_file_string)
        assert re.search(r"9075.0\s+9125.0\s+0.002\s+0.002\s+0.01\s+0.15\s+2\s+1.0", parameter_file_string)
