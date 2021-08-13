from enum import Enum

try:
    from enum import StrEnum
except ImportError:
    from backports.strenum import StrEnum


class LensModelParameterNameBase(StrEnum):
    pass


class LensModelParameterName(LensModelParameterNameBase):
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


class BinarySourceLensModelParameterName(LensModelParameterNameBase):
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
    PI_EX = 'piEx'
    PI_EY = 'piEy'
    T_0_S_2 = 't0s2'
    UMINS_2 = 'umins2'
    F_2_R_I = 'f2rI'
    F_2_MRPOW_I = 'f2MRpowI'
    F_2_R_V = 'f2rV'
    DT_E_21 = 'dt_E21'
    DTHETA = 'dtheta'
    TSTAR_2 = 'Tstar2'
    F_2_KPOW_I = 'f2KpowI'
    TCCH_1_MIN = 'tcch1_min'
    TCCH_1_MAX = 'tcch1_max'
    TCCH_2_MIN = 'tcch2_min'
    TCCH_2_MAX = 'tcch2_max'
    THEX_1_MIN = 'thex1_min'
    THEX_1_MAX = 'thex1_max'
    THEX_2_MIN = 'thex2_min'
    THEX_2_MAX = 'thex2_max'
    T_SBININV = 'T_Sbininv'
