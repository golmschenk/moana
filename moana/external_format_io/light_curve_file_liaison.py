"""
Code to interact with light curve files of various formats.
"""
from pathlib import Path
import pandas as pd

from moana.david_bennett_fit.light_curve import LightCurveFileLiaison as DavidBennettLightCurveFileLiaison, ColumnName


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
            ColumnName.MICROLENSING_HJD.value: ian_bond_data_frame['HJD'] - 2450000,
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

        :param kmt_tlc_input_path: The path to Ian Bond's file.
        :return: The light curve data frame.
        """
        kmt_tlc_data_frame = pd.read_csv(kmt_tlc_input_path, escapechar='#', delim_whitespace=True,
                                         skipinitialspace=True)
        kmt_tlc_data_frame.columns = kmt_tlc_data_frame.columns.str.strip()  # Remove whitespace in header
        david_bennett_data_frame = pd.DataFrame({
            ColumnName.MICROLENSING_HJD.value: kmt_tlc_data_frame['HJD'],
            ColumnName.FLUX.value: kmt_tlc_data_frame[r'\Delta_flux'],
            ColumnName.FLUX_ERROR.value: kmt_tlc_data_frame['error'],
            ColumnName.FULL_WIDTH_HALF_MAX.value: kmt_tlc_data_frame['FWHM']
        })
        return david_bennett_data_frame

    def convert_light_curve_file_from_lco_format_to_david_bennet_format(self, lco_input_path: Path,
                                                                        david_bennett_output_path: Path):
        david_bennett_data_frame = self.load_lco_light_curve(lco_input_path)
        DavidBennettLightCurveFileLiaison.save_light_curve_to_david_bennett_format_file(david_bennett_output_path,
                                                                                        david_bennett_data_frame)

    @staticmethod
    def load_lco_light_curve(lco_input_path: Path) -> pd.DataFrame:
        """
        Loads a light curve from LCO format.

        :param lco_input_path: The path to the LCO file.
        :return: The light curve data frame.
        """
        lco_data_frame = pd.read_csv(lco_input_path, delim_whitespace=True,
                                     names=['hjd', 'magnification', 'magnification_error'])
        david_bennett_data_frame = pd.DataFrame({
            ColumnName.MICROLENSING_HJD.value: lco_data_frame['hjd'] - 2450000,
            ColumnName.MAGNIFICATION.value: lco_data_frame['magnification'],
            ColumnName.MAGNIFICATION_ERROR.value: lco_data_frame['magnification_error']
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
                                        names=['microlensing_hjd', 'magnification', 'magnification_error'])
        david_bennett_data_frame = pd.DataFrame({
            ColumnName.MICROLENSING_HJD.value: dophot_data_frame['microlensing_hjd'],
            ColumnName.MAGNIFICATION.value: dophot_data_frame['magnification'],
            ColumnName.MAGNIFICATION_ERROR.value: dophot_data_frame['magnification_error']
        })
        david_bennett_data_frame = david_bennett_data_frame[
            david_bennett_data_frame[ColumnName.MAGNIFICATION.value] != 0
            ]
        return david_bennett_data_frame


if __name__ == '__main__':
    light_curve_file_liaison = LightCurveFileLiaison()
    light_curve_file_liaison.convert_light_curve_file_from_ian_bond_format_to_david_bennet_format(
        Path('data/mb20208/external_data/mb20208-MOA2R-10000.phot.dat.txt'),
        Path('data/mb20208/old_flat_directory_style_runs/lcMB20208.moa2r')
    )
    light_curve_file_liaison.convert_light_curve_file_from_ian_bond_format_to_david_bennet_format(
        Path('data/mb20208/external_data/mb20208-MOA2V-10000.phot.dat.txt'),
        Path('data/mb20208/old_flat_directory_style_runs/lcMB20208.moa2v')
    )
    light_curve_file_liaison.convert_light_curve_file_from_kmt_tlc_format_to_david_bennet_format(
        Path('data/mb20208/external_data/KMTA22_I.pysis.dflux'),
        Path('data/mb20208/old_flat_directory_style_runs/lcMB20208.kmtA22')
    )
