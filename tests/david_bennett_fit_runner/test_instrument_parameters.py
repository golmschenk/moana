import re
from pathlib import Path
from unittest.mock import Mock, patch
from astropy.coordinates import EarthLocation

from moana.david_bennett_fit.instrument_parameters import InstrumentParameters, MeasurementType

# noinspection SpellCheckingInspection
fake_david_bennett_parameter_file_content_lines = [
    "# daycausmin   daycausmax   deltcaus  delfine   gridUstar   hcut   iend    grid_rat\n",
    "  9075.0       9125.0         0.002    0.002     0.01       0.15    2      1.00\n",
    "# jclr  fudge  errmin  fmin    fmax    ald      bld      dayoff     sfx\n",
    "   0    1.0    0.014   0.01    1.10   0.6310   0.0000      0.000   'op'\n",
    "   1    1.0    0.014   0.01    1.10   0.7730   0.0000      0.000   'op'\n",
    "   2    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'ctio_r'\n",
    "   3    1.5    0.01    0.01    1.10   0.8200   0.0000      0.000   'ctio_b'\n",
    "   4    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'nz'\n",
    "   5    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'utso'\n",
    "   6    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'utso_v'\n",
    "   7    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'wised'\n",
    "   8    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'mso74n'\n",
    "   9    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'mso74'\n",
    "  10    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'wises'\n",
    "  11    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'lco1'\n",
    "  12    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'lco3'\n",
    "  13    1.500  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'mfuns'   -70.8146  -30.1654\n",
    "  14    1.5    0.01    0.01    1.10   0.6905   0.0000      0.000   'xe'\n",
    "  15    1.500  0.003  -1.e9    1.e9   0.5900   0.0000      0.000   'kum'     174.5247  -36.8064\n",
    "  16    1.500  0.003  -1.e9    1.e9   0.5900   0.0000      0.000   'pest'    115.7981  -31.9928\n",
    "  17    1.500  0.003  -1.e9    1.e9   0.5900   0.0000      0.000   'auck'    174.7769  -36.9061\n",
    "  18    1.500  0.003  -1.e9    1.e9   0.5900   0.0000      0.000   'fcov'    174.8942  -36.8953\n",
    "  19    1.500  0.003  -1.e9    1.e9   0.5900   0.0000      0.000   'pos'     177.891   -38.624\n",
    "  20    1.500  0.003  -1.e9    1.e9   0.5900   0.0000      0.000   'tur'     175.6539  -40.4119\n",
    "  21    1.219  0.003  -1.e9    1.e9   0.3042   0.0000      0.000   'mfunH'   -70.8047  -30.1683\n",
    "  22    1.500  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'oglem'   -70.702   -29.0081\n",
    "  23    1.000  0.003  -1.e9    1.e9   0.6730   0.0000      0.000   'mfunV'   -70.8047  -30.1683\n",
    "  24    1.301  0.003  -1.e9    1.e9   0.6730   0.0000      0.000   'ogleV'   -70.702   -29.0081\n",
    "  25    1.255  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'saao'     20.8107  -32.3794\n",
    "  26    1.000  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'perth'   115.859   -31.952\n",
    "  27    1.500  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'null'\n",
    "  28    1.500  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'mfun'    -70.8047  -30.1683\n",
    "  29    0.847  0.000  -1.e9    1.e9   0.6043   0.0000      0.000   'bron'     28.4456  -25.9133\n",
    "  30    1.500  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'ftni'   -156.2558   20.7075\n",
    "  31    1.233  0.003  -1.e9    1.e9   0.6043   0.0000      0.000   'ftsi'    149.4380  -31.2733\n",
    "  32    1.500  0.003  -1.e9    1.e9   0.5633   0.0000      0.000   'moa2r'   170.465   -43.9867\n",
    "  33    0.800  0.003  -1.e9    1.e9   0.6730   0.0000      0.000   'moa2v'   170.465   -43.9867\n",
    "  34    1.500  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'moa61I'  170.465   -43.9867\n",
    "  35    1.386  0.003  -1.e9    1.e9   0.6730   0.0000      0.000   'moa61V'  170.465   -43.9867\n",
    "  36    1.000  0.000  -1.e9    1.e9   0.5212   0.0000      0.000   'mfuni'   -70.8146  -30.1654\n",
    "  37    1.500  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'kmtA22'  -70.8048  -30.1674\n",
    "  38    1.180  0.003  -1.e9    1.e9   0.5212   0.0000      0.000   'teide'   -16.5097   28.300\n",
    "  39    1.500  0.003  -1.e9    1.e9   0.5900   0.0000      0.000   'kko'      21.667   -33.533\n",
    "  40    3.646  0.003  -1.e9    1.e9   0.6043   0.0000      0.000   'livi'    -17.8792   28.7624\n"
]


class TestInstrumentParameters:
    def test_can_load_parameters_list_from_david_bennett_parameter_file(self):
        with patch.object(Path, 'open') as stub_open:
            stub_read_lines = Mock(return_value=fake_david_bennett_parameter_file_content_lines)
            stub_open.return_value.__enter__.return_value = Mock(readlines=stub_read_lines)
            path = Path('')
            instrument_parameters_dictionary = InstrumentParameters.dictionary_from_david_bennett_parameter_file(path)
            assert instrument_parameters_dictionary['moa2r'].suffix == 'moa2r'
            assert instrument_parameters_dictionary['moa2r'].measurement_type == MeasurementType.FLUX
            assert instrument_parameters_dictionary['moa2r'].earth_location == EarthLocation.from_geodetic(
                lon=170.465, lat=-43.9867)
            assert instrument_parameters_dictionary['moa2r'].fudge_factor == 1.5

    def test_can_create_david_bennett_input_string_from_parameters_dictionary(self):
        instrument_parameters_list = [
            InstrumentParameters('moa2r', MeasurementType.FLUX),
            InstrumentParameters('moa2v', MeasurementType.FLUX, fudge_factor=1.2,
                                 earth_location=EarthLocation.from_geodetic(lon=170.465, lat=-43.9867)),
            InstrumentParameters('pest', MeasurementType.MAGNITUDE_21_BASED, fudge_factor=1.5)
        ]
        parameter_file_string = InstrumentParameters.david_bennett_parameter_file_string_from_list(
            instrument_parameters_list)
        assert re.search(r"30\s+1.0[^\n]+'moa2r'\n", parameter_file_string)
        assert re.search(r"31\s+1.2[^\n]+'moa2v'\s+170\.465\s+-43\.9867\n", parameter_file_string)
        assert re.search(r"15\s+1.5[^\n]+'pest'\n", parameter_file_string)
