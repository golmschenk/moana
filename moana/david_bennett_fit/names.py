import inspect

try:
    from enum import StrEnum
except ImportError:
    from backports.strenum import StrEnum
from typing import Optional, List


class NameElement(str):
    def __new__(cls, name: str, *args, **kwargs):
        value = name
        return str.__new__(cls, value)

    def __init__(self, name: str, david_bennett_name: Optional[str] = None, latex_string: Optional[str] = None,
                 unit_latex_string: Optional[str] = None):
        self.name: str = name
        self._david_bennett_name: Optional[str] = david_bennett_name
        self._latex_string: Optional[str] = latex_string
        self.units_latex_string: Optional[str] = unit_latex_string

    @property
    def david_bennett_name(self) -> str:
        if self._david_bennett_name is None:
            raise AttributeError(f'{self} name element has no david_bennett_name')
        return self._david_bennett_name

    @property
    def latex_string(self) -> str:
        if self._latex_string is None:
            raise AttributeError(f'{self} name element has no latex_string')
        return self._latex_string


class NameEnumBase:
    @classmethod
    def as_list(cls) -> List[NameElement]:
        parent_class = cls
        element_list = []
        while parent_class is not NameEnumBase:
            parent_class_element_list = [element for element in parent_class.__dict__.values()
                                         if isinstance(element, NameElement)]
            element_list = parent_class_element_list + element_list
            parent_bases = parent_class.__bases__
            assert len(parent_bases) == 1  # Only works for single parent enums at the moment.
            parent_class = parent_bases[0]
        return element_list

    @classmethod
    def element_from_david_bennett_name(cls, david_bennett_name: str) -> NameElement:
        for element in cls.as_list():
            try:
                if element.david_bennett_name == david_bennett_name:
                    return element
            except AttributeError:
                continue
        raise KeyError(f'david_bennett_name `{david_bennett_name}` not found in {cls}.')


class NameEnum(NameEnumBase):
    EINSTEIN_CROSSING_TIME = NameElement(name='einstein_crossing_time', latex_string=r't_\mathrm{E}', unit_latex_string='\mathrm{days}')
    EINSTEIN_RADIUS = NameElement(name='einstein_radius', latex_string=r'\theta_\mathrm{0}')
    CHI_SQUARED_STATISTIC = NameElement(name='chi_squared_statistic', david_bennett_name='chisq', latex_string=r'\chi^2')
    INVERSE_EINSTEIN_CROSSING_TIME = NameElement(name='inverse_einstein_crossing_time', david_bennett_name='1/t_E')
    MINIMUM_SEPARATION_TIME = NameElement(name='minimum_separation_time', david_bennett_name='t0', latex_string=r't_0', unit_latex_string='\mathrm{HJD\'}')
    MINIMUM_SEPARATION = NameElement(name='minimum_separation', david_bennett_name='umin', latex_string=r'u_0')
    MASS_RATIO = NameElement(name='mass_ratio', latex_string=r'q')
    SECONDARY_SEPARATION = NameElement(name='secondary_separation', david_bennett_name='sep', latex_string=r's')
    SECONDARY_SEPARATION_ANGLE = NameElement(name='secondary_separation_angle', david_bennett_name='theta', latex_string=r'\theta', unit_latex_string='\mathrm{rad}')
    SECONDARY_EPSILON = NameElement(name='secondary_epsilon', david_bennett_name='eps1')
    INVERSE_T_BIN = NameElement(name='inverse_t_bin', david_bennett_name='1/Tbin')
    V_SEPARATION = NameElement(name='v_separation', david_bennett_name='v_sep')
    SOURCE_RADIUS_CROSSING_TIME = NameElement(name='source_radius_crossing_time', david_bennett_name='Tstar', latex_string=r't_*', unit_latex_string='\mathrm{days}')
    T_FIX = NameElement(name='t_fix', david_bennett_name='t_fix')
    PI_ER = NameElement(name='pi_er', david_bennett_name='piEr', latex_string=r'r_{\pi_{\mathrm{E}}}')
    PI_ETH = NameElement(name='pi_eth', david_bennett_name='pieth', latex_string=r'\theta_{\pi_{\mathrm{E}}}', unit_latex_string='\mathrm{rad}')
    PI_EX = NameElement(name='pi_ex', david_bennett_name='piEx')
    PI_EY = NameElement(name='pi_ey', david_bennett_name='piEy')
    SOURCE_2_MINIMUM_SEPARATION_TIME = NameElement(name='source_2_minimum_separation_time', david_bennett_name='t0s2', latex_string=r't_{0, s_{2}}')
    SOURCE_2_MINIMUM_SEPARATION = NameElement(name='source_2_minimum_separation', david_bennett_name='umins2', latex_string=r'u_{0, s_{2}}')
    I_BAND_FLUX_FRACTION_FROM_SECOND_SOURCE = NameElement(name='i_band_flux_fraction_from_second_source', david_bennett_name='f2rI', latex_string=r'f_{I, s_{2}}')
    F_2_MRPOW_I = NameElement(name='f_2_mrpow_i', david_bennett_name='f2MRpowI')
    R_BAND_FLUX_FRACTION_FROM_SECOND_SOURCE = NameElement(name='r_band_flux_fraction_from_second_source', david_bennett_name='f2rV', latex_string=r'f_{R, s_{2}}')
    DT_E_21 = NameElement(name='dt_e_21', david_bennett_name='dt_E21')
    DTHETA = NameElement(name='dtheta', david_bennett_name='dtheta')
    TSTAR_2 = NameElement(name='tstar_2', david_bennett_name='Tstar2')
    F_2_KPOW_I = NameElement(name='f_2_kpow_i', david_bennett_name='f2KpowI')
    TCCH_1_MIN = NameElement(name='tcch_1_min', david_bennett_name='tcch1_min')
    TCCH_1_MAX = NameElement(name='tcch_1_max', david_bennett_name='tcch1_max')
    TCCH_2_MIN = NameElement(name='tcch_2_min', david_bennett_name='tcch2_min')
    TCCH_2_MAX = NameElement(name='tcch_2_max', david_bennett_name='tcch2_max')
    THEX_1_MIN = NameElement(name='thex_1_min', david_bennett_name='thex1_min')
    THEX_1_MAX = NameElement(name='thex_1_max', david_bennett_name='thex1_max')
    THEX_2_MIN = NameElement(name='thex_2_min', david_bennett_name='thex2_min')
    THEX_2_MAX = NameElement(name='thex_2_max', david_bennett_name='thex2_max')
    T_SBININV = NameElement(name='t_sbininv', david_bennett_name='T_Sbininv')


class LensModelParameterNameEnum(NameEnumBase):
    INVERSE_EINSTEIN_CROSSING_TIME = NameEnum.INVERSE_EINSTEIN_CROSSING_TIME
    MINIMUM_SEPARATION_TIME = NameEnum.MINIMUM_SEPARATION_TIME
    MINIMUM_SEPARATION = NameEnum.MINIMUM_SEPARATION
    SECONDARY_SEPARATION = NameEnum.SECONDARY_SEPARATION
    SECONDARY_THETA = NameEnum.SECONDARY_SEPARATION_ANGLE
    SECONDARY_EPSILON = NameEnum.SECONDARY_EPSILON
    INVERSE_T_BIN = NameEnum.INVERSE_T_BIN
    V_SEPARATION = NameEnum.V_SEPARATION
    SOURCE_RADIUS_CROSSING_TIME = NameEnum.SOURCE_RADIUS_CROSSING_TIME
    T_FIX = NameEnum.T_FIX


class BinaryLensModelParameterNameEnum(LensModelParameterNameEnum):
    PI_EX = NameEnum.PI_EX
    PI_EY = NameEnum.PI_EY


class BinarySourceModelParameterNameEnum(LensModelParameterNameEnum):
    PI_EX = NameEnum.PI_EX
    PI_EY = NameEnum.PI_EY
    SOURCE_2_MINIMUM_SEPARATION_TIME = NameEnum.SOURCE_2_MINIMUM_SEPARATION_TIME
    SOURCE_2_MINIMUM_SEPARATION = NameEnum.SOURCE_2_MINIMUM_SEPARATION
    I_BAND_FLUX_FRACTION_FROM_SECOND_SOURCE = NameEnum.I_BAND_FLUX_FRACTION_FROM_SECOND_SOURCE
    F_2_MRPOW_I = NameEnum.F_2_MRPOW_I
    R_BAND_FLUX_FRACTION_FROM_SECOND_SOURCE = NameEnum.R_BAND_FLUX_FRACTION_FROM_SECOND_SOURCE
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
