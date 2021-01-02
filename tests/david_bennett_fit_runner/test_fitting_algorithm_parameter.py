import re
from pathlib import Path
from unittest.mock import Mock, patch

from moana.david_bennett_fit.fitting_parameter import FittingAlgorithmParameters


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
        assert False  # TODO: Finish test.
        # instrument_parameters_list = [
        #     InstrumentParameters('moa2r', MeasurementType.FLUX),
        #     InstrumentParameters('moa2v', MeasurementType.FLUX, fudge_factor=1.2,
        #                          earth_location=EarthLocation.from_geodetic(lon=170.465, lat=-43.9867)),
        #     InstrumentParameters('pest', MeasurementType.MAGNITUDE_21_BASED, fudge_factor=1.5)
        # ]
        # parameter_file_string = InstrumentParameters.david_bennett_parameter_file_string_from_list(
        #     instrument_parameters_list)
        # assert re.search(r"30\s+1.0[^\n]+'moa2r'\n", parameter_file_string)
        # assert re.search(r"31\s+1.2[^\n]+'moa2v'\s+170\.465\s+-43\.9867\n", parameter_file_string)
        # assert re.search(r"15\s+1.5[^\n]+'pest'\n", parameter_file_string)
