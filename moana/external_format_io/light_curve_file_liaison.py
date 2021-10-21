"""
Code to interact with light curve files of various formats.
"""
import re
from io import StringIO
from pathlib import Path
import pandas as pd

from moana.light_curve import LightCurve as DavidBennettLightCurveFileLiaison, ColumnName


class LightCurveFileLiaison:
    @staticmethod
    def load_ian_bond_light_curve(ian_bond_input_path: Path) -> pd.DataFrame:
        """
        Loads a light curve from Ian Bond's format.

        :param ian_bond_input_path: The path to Ian Bond's file.
        :return: The light curve data frame.
        """
        # noinspection SpellCheckingInspection
        ian_bond_data_frame = pd.read_csv(ian_bond_input_path, delim_whitespace=True, skipinitialspace=True,
                                          comment='#', names=['HJD', 'Flux', 'Flux_err', 'obs id', 'mag', 'merr',
                                                              'fwhm', 'background', 'photometric scale'])
        david_bennett_data_frame = pd.DataFrame({
            ColumnName.TIME__MICROLENSING_HJD.value: ian_bond_data_frame['HJD'] - 2450000,
            ColumnName.FLUX.value: ian_bond_data_frame['Flux'],
            ColumnName.FLUX_ERROR.value: ian_bond_data_frame['Flux_err'],
            ColumnName.FULL_WIDTH_HALF_MAX.value: ian_bond_data_frame['fwhm']
        })
        return david_bennett_data_frame

    def convert_light_curve_file_from_ian_bond_format_to_david_bennet_format(self, ian_bond_input_path: Path,
                                                                             david_bennett_output_path: Path):
        light_curve_data_frame = self.load_ian_bond_light_curve(ian_bond_input_path)
        DavidBennettLightCurveFileLiaison.save_light_curve_to_david_bennett_format_file(david_bennett_output_path,
                                                                                        light_curve_data_frame)

    def convert_light_curve_file_from_kmt_tlc_format_to_david_bennet_format(self, kmt_tlc_input_path: Path,
                                                                            david_bennett_output_path: Path):
        light_curve_data_frame = self.load_kmt_tlc_light_curve(kmt_tlc_input_path)
        DavidBennettLightCurveFileLiaison.save_light_curve_to_david_bennett_format_file(david_bennett_output_path,
                                                                                        light_curve_data_frame)

    @staticmethod
    def load_kmt_tlc_light_curve(kmt_tlc_input_path: Path) -> pd.DataFrame:
        """
        Loads a light curve from KMT's TLC format.

        :param kmt_tlc_input_path: The path to KMT file.
        :return: The light curve data frame.
        """
        kmt_tlc_data_frame = pd.read_csv(kmt_tlc_input_path, escapechar='#', delim_whitespace=True,
                                         skipinitialspace=True)
        kmt_tlc_data_frame.columns = kmt_tlc_data_frame.columns.str.strip()  # Remove whitespace in header
        david_bennett_data_frame = pd.DataFrame({
            ColumnName.TIME__MICROLENSING_HJD.value: kmt_tlc_data_frame['HJD'],
            ColumnName.FLUX.value: kmt_tlc_data_frame[r'\Delta_flux'],
            ColumnName.FLUX_ERROR.value: kmt_tlc_data_frame['error'],
            ColumnName.FULL_WIDTH_HALF_MAX.value: kmt_tlc_data_frame['FWHM']
        })
        return david_bennett_data_frame

    def convert_light_curve_file_from_lco_format_to_david_bennet_format(self, lco_input_path: Path,
                                                                        david_bennett_output_path: Path):
        david_bennett_data_frame = self.load_saao_light_curve(lco_input_path)
        DavidBennettLightCurveFileLiaison.save_light_curve_to_david_bennett_format_file(david_bennett_output_path,
                                                                                        david_bennett_data_frame)

    @staticmethod
    def load_saao_light_curve(saao_input_path: Path) -> pd.DataFrame:
        """
        Loads a light curve from SAAO format.

        :param saao_input_path: The path to the SAAO file.
        :return: The light curve data frame.
        """
        saao_data_frame = pd.read_csv(saao_input_path, delim_whitespace=True,
                                      names=['hjd', 'magnitude', 'magnitude_error'], comment='#')
        david_bennett_data_frame = pd.DataFrame({
            ColumnName.TIME__MICROLENSING_HJD.value: saao_data_frame['hjd'] - 2450000,
            ColumnName.MAGNITUDE.value: saao_data_frame['magnitude'],
            ColumnName.MAGNITUDE_ERROR.value: saao_data_frame['magnitude_error']
        })
        return david_bennett_data_frame

    def convert_light_curve_file_from_dophot_format_to_david_bennet_format(self, dophot_input_path: Path,
                                                                           david_bennett_output_path: Path):
        light_curve_data_frame = self.load_dophot_light_curve(dophot_input_path)
        light_curve_data_frame.to_csv(david_bennett_output_path, header=False, index=False, sep=' ')

    @staticmethod
    def load_dophot_light_curve(dophot_input_path: Path) -> pd.DataFrame:
        """
        Loads a light curve from DoPhot format.

        :param dophot_input_path: The path to the DoPhot file.
        :return: The light curve data frame.
        """
        dophot_data_frame = pd.read_csv(dophot_input_path, delim_whitespace=True, skipinitialspace=True,
                                        comment='#', usecols=[0, 1, 2],
                                        names=['microlensing_hjd', 'magnitude', 'magnitude_error'])
        david_bennett_data_frame = pd.DataFrame({
            ColumnName.TIME__MICROLENSING_HJD.value: dophot_data_frame['microlensing_hjd'],
            ColumnName.MAGNITUDE.value: dophot_data_frame['magnitude'],
            ColumnName.MAGNITUDE_ERROR.value: dophot_data_frame['magnitude_error']
        })
        david_bennett_data_frame = david_bennett_data_frame[
            david_bennett_data_frame[ColumnName.MAGNITUDE.value] != 0
            ]
        return david_bennett_data_frame

    @staticmethod
    def load_pysis_light_curve_data_frame(pysis_file_path: Path) -> pd.DataFrame:
        """
        Loads a pysis format file in the project light curve data frame format.

        :param pysis_file_path: The path to the pysis file.
        :return: The data frame with the light curve information.
        """
        with pysis_file_path.open() as pysis_file:
            pysis_file_content = pysis_file.read()
        pysis_file_content = re.sub(r'[ ]{2,}', ' nan ', pysis_file_content)  # Missing values are multiple spaces.
        pysis_string_io = StringIO(pysis_file_content)
        light_curve_data_frame = pd.read_csv(pysis_string_io, delim_whitespace=True, header=None,
                                             usecols=[1, 2, 3],
                                             names=[ColumnName.MAGNITUDE.value,
                                                    ColumnName.MAGNITUDE_ERROR.value,
                                                    ColumnName.TIME__MICROLENSING_HJD.value])
        return light_curve_data_frame

    @staticmethod
    def load_omega_light_curve_data_frame(omega_file_path: Path) -> pd.DataFrame:
        """
        Loads a omega format file in the project light curve data frame format.

        :param omega_file_path: The path to the pysis file.
        :return: The data frame with the light curve information.
        """
        light_curve_data_frame = pd.read_csv(omega_file_path, delim_whitespace=True, skipinitialspace=True,
                                             comment='#', names=[ColumnName.TIME__HJD.value,
                                                                 ColumnName.MAGNITUDE.value,
                                                                 ColumnName.MAGNITUDE_ERROR.value])
        light_curve_data_frame[ColumnName.TIME__MICROLENSING_HJD.value] = \
            light_curve_data_frame[ColumnName.TIME__HJD.value] - 2450000
        light_curve_data_frame.drop(columns=[ColumnName.TIME__HJD.value])
        return light_curve_data_frame


if __name__ == '__main__':
    light_curve_file_liaison = LightCurveFileLiaison()
    light_curve_file_liaison.load_omega_light_curve_data_frame(
        Path('data/mb20208/external_data/OMEGA_MOA_2020_BLG_208_gp.dat')
    )
