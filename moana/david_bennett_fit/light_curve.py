"""
Code for working with David Bennett's light curve format.
"""

class LightCurveFileLiaison:
    """
    A class for working with David Bennett's light curve format.
    """
    @staticmethod
    def save_light_curve_to_david_bennett_format_file(path, light_curve_data_frame):
        """
        Saves a light curve data frame to a file of the format expected by David Bennett's code.

        :param path: The path to the output file.
        :param light_curve_data_frame: The light curve data frame.
        """
        light_curve_data_frame.to_csv(path, header=False, index=False, sep=' ')
