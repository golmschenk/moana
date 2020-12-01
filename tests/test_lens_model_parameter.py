import re
import pytest
from pathlib import Path
from unittest.mock import patch, Mock

from moana.david_bennett_fit.lens_model_parameter import LensModelParameter


# noinspection SpellCheckingInspection
fake_david_bennett_input_file_contents = ["Fit to binary microlens for star MB20208 fit series run_\n",
                                          "  1 '1/t_E'  0.50782170131E-01   0.00003\n",
                                          "  2 't0'     9101.0              0.001\n",
                                          "  3 'umin'   0.26456270222E-01   0.00005\n",
                                          "  4 'sep'    1.3709031845        0.00005  -5.0 5.0\n",
                                          "  5 'theta'  3.1102936551267932  0.00005  -7.0 7.0\n",
                                          "  6 'eps1'   0.20588534422E-03   1.e-5 0.00000001 0.9\n",
                                          "  7 '1/Tbin' 0.0000000000        0.\n",
                                          "  8 'v_sep'  0.0000000000        0.\n",
                                          "  9 'Tstar'  0.18737960701       0.00004 0.000001  10.0\n",
                                          " 10 't_fix'  9100.8972158        0.\n",
                                          " 11 'piEr'   0.0000000000        0.\n",
                                          " 12 'pieth'  0.0000000000        0.\n",
                                          "\n",
                                          "MB20208\n",
                                          "run_\n",
                                          "no limb\n",
                                          "17 53 24.6311 -32 40 20.3141\n",
                                          "0\n",
                                          "SET EPS   1.e-5\n",
                                          "DSEEK      3000\n",
                                          "SET ERR     0.2\n",
                                          "DSEEK      3000\n",
                                          "EXIT\n"]


class TestLensModelParameter:
    def test_can_load_parameters_from_david_bennett_input_file(self):
        with patch.object(Path, 'open') as stub_open:
            stub_read_lines = Mock(return_value=fake_david_bennett_input_file_contents)
            stub_open.return_value.__enter__.return_value = Mock(readlines=stub_read_lines)
            path = Path('')
            lens_model_parameter_dictionary = LensModelParameter.dictionary_from_david_bennett_input_file(path)
            assert lens_model_parameter_dictionary['t0'].value == 9101.0
            assert lens_model_parameter_dictionary['sep'].temperature == 0.00005
            assert lens_model_parameter_dictionary['theta'].minimum_limit == -7.0
            assert lens_model_parameter_dictionary['theta'].maximum_limit == 7.0

    def test_can_create_david_bennett_input_string_from_parameters_dictionary(self):
        parameter_dictionary = {
            'v_sep': LensModelParameter(value=1, temperature=2),
            '1/t_E': LensModelParameter(value=1, temperature=2),
            't0': LensModelParameter(value=1, temperature=2),
            'umin': LensModelParameter(value=1, temperature=2),
            'theta': LensModelParameter(value=1, temperature=2),
            'eps1': LensModelParameter(value=1, temperature=2),
            '1/Tbin': LensModelParameter(value=1, temperature=1e-8),
            'sep': LensModelParameter(value=1, temperature=2, minimum_limit=0, maximum_limit=4),
            'Tstar': LensModelParameter(value=1, temperature=2),
            't_fix': LensModelParameter(value=1, temperature=2, minimum_limit=1e-7, maximum_limit=1e2),
            'piEr': LensModelParameter(value=1, temperature=2),
            'pieth': LensModelParameter(value=1, temperature=2)
        }
        input_string = LensModelParameter.david_bennett_input_string_from_dictionary(parameter_dictionary)
        assert re.search(r"4\s+'sep'\s+1.0\s+2.0\s+0.0\s+4.0\n", input_string)
        assert re.search(r"7\s+'1/Tbin'\s+1.0\s+1e-08\n", input_string)

    def test_create_david_bennett_input_string_from_parameters_dictionary_fails_for_missing_parameter(self):
        parameter_dictionary = {
            'v_sep': LensModelParameter(value=1, temperature=2),
            '1/t_E': LensModelParameter(value=1, temperature=2),
            't0': LensModelParameter(value=1, temperature=2),
            'umin': LensModelParameter(value=1, temperature=2),
            'theta': LensModelParameter(value=1, temperature=2)
        }
        with pytest.raises(KeyError):
            LensModelParameter.david_bennett_input_string_from_dictionary(parameter_dictionary)

    def test_create_david_bennett_input_string_from_parameters_dictionary_fails_for_unknown_parameter(self):
        parameter_dictionary = {
            'v_sep': LensModelParameter(value=1, temperature=2),
            '1/t_E': LensModelParameter(value=1, temperature=2),
            't0': LensModelParameter(value=1, temperature=2),
            'umin': LensModelParameter(value=1, temperature=2),
            'theta': LensModelParameter(value=1, temperature=2),
            'eps1': LensModelParameter(value=1, temperature=2),
            '1/Tbin': LensModelParameter(value=1, temperature=2),
            'sep': LensModelParameter(value=1, temperature=2, minimum_limit=0, maximum_limit=4),
            'Tstar': LensModelParameter(value=1, temperature=2),
            't_fix': LensModelParameter(value=1, temperature=2),
            'piEr': LensModelParameter(value=1, temperature=2),
            'pieth': LensModelParameter(value=1, temperature=2),
            'unknown_name': LensModelParameter(value=1, temperature=2)
        }
        with pytest.raises(AssertionError):
            LensModelParameter.david_bennett_input_string_from_dictionary(parameter_dictionary)
