import numpy as np
import numpy.ma as ma
from matplotlib import pyplot as plt
from matplotlib.colors import LogNorm

from magnification_pattern.luckylensing.luckylensing import rayshoot
from magnification_pattern.luckylensing.luckylensing import lensconfig


def main():
    # Map of PSPL model
    number_of_x_pixels = int(2 ** 14)
    number_of_y_pixels = int(2 ** 14)

    lens1 = [(0, 0, 1.0)]
    full_plotting_region = (-0.2, -1.2, 2.5, 1.2)
    single_lens_magnification_pattern = rayshoot(lens1, full_plotting_region, number_of_x_pixels, number_of_y_pixels, num_threads=4)

    # Map of PSBL model
    sep = -0.475423  # <0 if lower mass at (sep, 0).
    q = 0.568450e-2
    binary_lens = lensconfig.binary_lenses(sep, q)
    magnification_pattern_l2 = rayshoot(binary_lens, full_plotting_region, number_of_x_pixels, number_of_y_pixels, num_threads=4)

    # Map of the central caustic
    central_region = (-0.012, -0.004, 0.004, 0.004)
    number_of_x_pixels = 4 * 1024
    number_of_y_pixels = 4 * 512
    central_magnification_pattern = rayshoot(binary_lens, central_region, number_of_x_pixels, number_of_y_pixels, num_threads=4)

    plt.clf()
    plt.imshow(central_magnification_pattern, cmap="hot", origin='lower',
               norm=LogNorm(vmin=np.min(central_magnification_pattern), vmax=np.max(central_magnification_pattern)),
               extent=[central_region[0], central_region[2], central_region[1], central_region[3]])
    plt.colorbar()
    plt.show()

    magnification_difference = magnification_pattern_l2 - single_lens_magnification_pattern

    masked_magnification_difference = ma.masked_where(
        (magnification_difference < -0.04) | (magnification_difference > 0.04), magnification_difference)
    masked_magnification_difference.fill_value = 0

    plt.clf()
    plt.imshow(masked_magnification_difference, cmap="coolwarm", origin='lower',
               extent=[full_plotting_region[0], full_plotting_region[2], full_plotting_region[1], full_plotting_region[3]])

    plt.colorbar()

    plt.show()


if __name__ == '__main__':
    main()
