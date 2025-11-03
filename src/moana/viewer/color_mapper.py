import itertools
import random

from bokeh import palettes
from bokeh.colors import Color


class ColorMapper:
    fit_colors = [element for element in itertools.chain.from_iterable(
        itertools.zip_longest(palettes.Greys[5][:4], palettes.Reds[5][:4])) if element]
    unshuffled_instrument_colors = list(palettes.Category20[20])
    random.seed(3)
    instrument_colors = random.sample(unshuffled_instrument_colors, len(unshuffled_instrument_colors))
    fit_name_to_color_dictionary = {}
    instrument_to_color_dictionary = {}

    def get_instrument_color(self, instrument_suffix: str) -> Color:
        if instrument_suffix not in self.instrument_to_color_dictionary:
            self.instrument_to_color_dictionary[instrument_suffix] = self.instrument_colors.pop(0)
        return self.instrument_to_color_dictionary[instrument_suffix]

    def get_fit_color(self, fit_name: str) -> Color:
        if fit_name not in self.fit_name_to_color_dictionary:
            self.fit_name_to_color_dictionary[fit_name] = self.fit_colors.pop(0)
        return self.fit_name_to_color_dictionary[fit_name]
