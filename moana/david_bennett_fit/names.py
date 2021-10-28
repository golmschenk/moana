import inspect

try:
    from enum import StrEnum
except ImportError:
    from backports.strenum import StrEnum
from typing import Optional, List


class LensModelParameterNameElement(str):
    def __new__(cls, name: str, *args, **kwargs):
        value = name
        return str.__new__(cls, value)

    def __init__(self, name: str, david_bennett_name: Optional[str] = None, latex_string: Optional[str] = None):
        self.name: str = name
        self.david_bennett_name: Optional[str] = david_bennett_name
        self.latex_string: Optional[str] = latex_string


class NameEnumBase:
    @classmethod
    def as_list(cls) -> List[LensModelParameterNameElement]:
        member_list = inspect.getmembers(cls)
        element_list = [member[1] for member in member_list if isinstance(member[1], LensModelParameterNameElement)]
        return element_list

    @classmethod
    def element_from_david_bennett_name(cls, david_bennett_name: str) -> LensModelParameterNameElement:
        for element in cls.as_list():
            if element.david_bennett_name == david_bennett_name:
                return element
        raise KeyError(f'david_bennett_name `{david_bennett_name}` not found in {cls}.')


class NameEnum(NameEnumBase):
    INVERSE_EINSTEIN_CROSSING_TIME = LensModelParameterNameElement(name='inverse_einstein_crossing_time', david_bennett_name='1/t_E')
    EINSTEIN_CROSS_TIME = LensModelParameterNameElement(name='einstein_crossing_time', latex_string=r't_\mathrm{E}')
    MINIMUM_APPROACH_TIME = LensModelParameterNameElement(name='minimum_approach_time', david_bennett_name='t0')
    MINIMUM_ANGULAR_SEPARATION = LensModelParameterNameElement(name='minimum_angular_separation', david_bennett_name='umin')
    SECONDARY_SEPARATION = LensModelParameterNameElement(name='secondary_separation', david_bennett_name='sep')
    SECONDARY_THETA = LensModelParameterNameElement(name='secondary_theta', david_bennett_name='theta')
    SECONDARY_EPSILON = LensModelParameterNameElement(name='secondary_epsilon', david_bennett_name='eps1')
    INVERSE_T_BIN = LensModelParameterNameElement(name='inverse_t_bin', david_bennett_name='1/Tbin')
    V_SEPARATION = LensModelParameterNameElement(name='v_separation', david_bennett_name='v_sep')
    T_STAR = LensModelParameterNameElement(name='t_star', david_bennett_name='Tstar')
    T_FIX = LensModelParameterNameElement(name='t_fix', david_bennett_name='t_fix')
    PI_ER = LensModelParameterNameElement(name='pi_er', david_bennett_name='piEr')
    PI_ETH = LensModelParameterNameElement(name='pi_eth', david_bennett_name='pieth')
    PI_EX = LensModelParameterNameElement(name='pi_ex', david_bennett_name='piEx')
    PI_EY = LensModelParameterNameElement(name='pi_ey', david_bennett_name='piEy')
    T_0_S_2 = LensModelParameterNameElement(name='t_0_s_2', david_bennett_name='t0s2')
    UMINS_2 = LensModelParameterNameElement(name='umins_2', david_bennett_name='umins2')
    F_2_R_I = LensModelParameterNameElement(name='f_2_r_i', david_bennett_name='f2rI')
    F_2_MRPOW_I = LensModelParameterNameElement(name='f_2_mrpow_i', david_bennett_name='f2MRpowI')
    F_2_R_V = LensModelParameterNameElement(name='f_2_r_v', david_bennett_name='f2rV')
    DT_E_21 = LensModelParameterNameElement(name='dt_e_21', david_bennett_name='dt_E21')
    DTHETA = LensModelParameterNameElement(name='dtheta', david_bennett_name='dtheta')
    TSTAR_2 = LensModelParameterNameElement(name='tstar_2', david_bennett_name='Tstar2')
    F_2_KPOW_I = LensModelParameterNameElement(name='f_2_kpow_i', david_bennett_name='f2KpowI')
    TCCH_1_MIN = LensModelParameterNameElement(name='tcch_1_min', david_bennett_name='tcch1_min')
    TCCH_1_MAX = LensModelParameterNameElement(name='tcch_1_max', david_bennett_name='tcch1_max')
    TCCH_2_MIN = LensModelParameterNameElement(name='tcch_2_min', david_bennett_name='tcch2_min')
    TCCH_2_MAX = LensModelParameterNameElement(name='tcch_2_max', david_bennett_name='tcch2_max')
    THEX_1_MIN = LensModelParameterNameElement(name='thex_1_min', david_bennett_name='thex1_min')
    THEX_1_MAX = LensModelParameterNameElement(name='thex_1_max', david_bennett_name='thex1_max')
    THEX_2_MIN = LensModelParameterNameElement(name='thex_2_min', david_bennett_name='thex2_min')
    THEX_2_MAX = LensModelParameterNameElement(name='thex_2_max', david_bennett_name='thex2_max')
    T_SBININV = LensModelParameterNameElement(name='t_sbininv', david_bennett_name='T_Sbininv')


class LensModelParameterNameEnum(NameEnumBase):
    INVERSE_EINSTEIN_CROSSING_TIME = NameEnum.INVERSE_EINSTEIN_CROSSING_TIME
    MINIMUM_APPROACH_TIME = NameEnum.MINIMUM_APPROACH_TIME
    MINIMUM_ANGULAR_SEPARATION = NameEnum.MINIMUM_ANGULAR_SEPARATION
    SECONDARY_SEPARATION = NameEnum.SECONDARY_SEPARATION
    SECONDARY_THETA = NameEnum.SECONDARY_THETA
    SECONDARY_EPSILON = NameEnum.SECONDARY_EPSILON
    INVERSE_T_BIN = NameEnum.INVERSE_T_BIN
    V_SEPARATION = NameEnum.V_SEPARATION
    T_STAR = NameEnum.T_STAR
    T_FIX = NameEnum.T_FIX


class BinaryLensModelParameterNameEnum(LensModelParameterNameEnum):
    PI_ER = NameEnum.PI_ER
    PI_ETH = NameEnum.PI_ETH


class BinarySourceModelParameterNameEnum(LensModelParameterNameEnum):
    PI_EX = NameEnum.PI_EX
    PI_EY = NameEnum.PI_EY
    T_0_S_2 = NameEnum.T_0_S_2
    UMINS_2 = NameEnum.UMINS_2
    F_2_R_I = NameEnum.F_2_R_I
    F_2_MRPOW_I = NameEnum.F_2_MRPOW_I
    F_2_R_V = NameEnum.F_2_R_V
    DT_E_21 = NameEnum.DT_E_21
    DTHETA = NameEnum.DTHETA
    TSTAR_2 = NameEnum.TSTAR_2
    F_2_KPOW_I = NameEnum.F_2_KPOW_I
    TCCH_1_MIN = NameEnum.TCCH_1_MIN
    TCCH_1_MAX = NameEnum.TCCH_1_MAX
    TCCH_2_MIN = NameEnum.TCCH_2_MIN
    TCCH_2_MAX = NameEnum.TCCH_2_MAX
    THEX_1_MIN = NameEnum.THEX_1_MIN
    THEX_1_MAX = NameEnum.THEX_1_MAX
    THEX_2_MIN = NameEnum.THEX_2_MIN
    THEX_2_MAX = NameEnum.THEX_2_MAX
    T_SBININV = NameEnum.T_SBININV
