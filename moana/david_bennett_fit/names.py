from enum import Enum


class LensModelParameterName(Enum):
    # TODO: These need better names
    INVERSE_EINSTEIN_CROSSING_TIME = '1/t_E'
    MINIMUM_APPROACH_TIME = 't0'
    MINIMUM_APPROACH_DISTANCE = 'umin'
    SECONDARY_SEPARATION = 'sep'
    SECONDARY_THETA = 'theta'
    SECONDARY_EPSILON = 'eps1'
    INVERSE_T_BIN = '1/Tbin'
    V_SEPARATION = 'v_sep'
    T_STAR = 'Tstar'
    T_FIX = 't_fix'
    PI_ER = 'piEr'
    PI_ETH = 'pieth'