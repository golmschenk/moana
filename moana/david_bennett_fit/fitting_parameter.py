from enum import Enum


# noinspection SpellCheckingInspection
class FittingParameterName(Enum):
    # TODO: These need better names
    DAY_CAUS_MIN = 'daycausmin'
    DAY_CAUS_MAX = 'daycausmax'
    DELT_CAUS = 'deltcaus'
    DEL_FINE = 'delfine'
    GRID_U_STAR = 'gridUstar'
    H_CUT = 'hcut'
    I_END = 'iend'
    GRID_RATIO = 'grid_rat'
