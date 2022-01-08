import logging
import os
import struct
import sys
from abc import ABC, abstractmethod
from typing import Any, Dict

import sysctl

logger = logging.getLogger(__name__)


class Variable(ABC):
    """
    A user defines a variable with its "name" and a way to fetch its value.
    """

    def __init__(self, name: str, params: Dict):
        assert name
        self._name = name
        self._value = None
        self._last_value = None

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other) -> bool:
        return self._name == other._name

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Any:
        return self._value

    @property
    def last_value(self) -> Any:
        return self._last_value

    def new_value(self) -> Any:
        self._last_value = self._value
        self._value = self._fetch_value()
        return self._value

    @abstractmethod
    def _fetch_value(self) -> Any:
        return self._value


class SyscmdVariable(Variable):
    """
    A user defines a variable with its "name" and sysctl name for its value.
    """

    def __init__(self, name: str, params: Dict):
        super().__init__(name, params)

        self._cmd = params["syscmd"]
        self._last_value = self._value = self._fetch_value()

    def _fetch_value(self) -> Any:
        return os.popen(self._cmd).read().strip()


TYPE = {
    # "node": None,
    "integer": "i",
    # "string": None,
    "int64_t": "q",
    # "opaque": None,
    "unsigned integer": "I",
    "long integer": "l",
    "long": "l",
    "unsigned long": "L",
    "uint64_t": "Q",
    "uint8_t": "B",
    "uint16_t": "H",
    "int8_t": "b",
    "int16_t": "h",
    "int32_t": "i",
    "uint32_t": "I",
}

VMTOTAL = [
    ("uint64_t", "t_vm"),  #     /* total virtual memory */
    ("uint64_t", "t_avm"),  #    /* active virtual memory */
    ("uint64_t", "t_rm"),  #     /* total real memory in use */
    ("uint64_t", "t_arm"),  #    /* active real memory */
    ("uint64_t", "t_vmshr"),  #  /* shared virtual memory */
    ("uint64_t", "t_avmshr"),  # /* active shared virtual memory */
    ("uint64_t", "t_rmshr"),  #  /* shared real memory */
    ("uint64_t", "t_armshr"),  # /* active shared real memory */
    ("uint64_t", "t_free"),  #   /* free memory pages */
    ("int16_t", "t_rq"),  #      /* length of the run queue */
    ("int16_t", "t_dw"),  #      /* threads in ``disk wait'' (neg priority) */
    ("int16_t", "t_pw"),  #      /* threads in page wait */
    ("int16_t", "t_sl"),  #      /* threads sleeping in core */
    ("int16_t", "t_sw"),  #      /* swapped out runnable/short block threads */
]

LOADAVG = [
    ("uint32_t", "1min"),
    ("uint32_t", "3min"),
    ("uint32_t", "15min"),
    ("long", "scale"),
]


class SysctlVariable(Variable):
    """
    A user defines a variable with its "name" and sysctl name for its value.
    """

    def __init__(self, name: str, params: Dict):
        super().__init__(name, params)

        self._sysctl_name = params["sysctl"]
        ctl = SysctlVariable._verify_sysctl(self._sysctl_name)
        self._last_value = self._value = SysctlVariable.extract(ctl)

    def _fetch_value(self) -> Any:
        # Sysctl caches and thus need a new instance each time
        ctl = sysctl.filter(self._sysctl_name)[0]
        return SysctlVariable.extract(ctl)

    @staticmethod
    def extract(ctl: "Sysctl") -> Any:
        if ctl.type == 10:  # CTLTYPE_U8
            offset = 1
        elif ctl.type == 11:  # CTLTYPE_U16
            offset = 2
        elif ctl.type == 15:  # CTLTYPE_U32
            offset = 4
        elif ctl.type == 5:  # CTLTYPE_U32
            return SysctlVariable.extract_struct(ctl)
        else:
            return ctl.value
        return int.from_bytes(ctl.value[0:offset], sys.byteorder, signed=False)

    @staticmethod
    def extract_loadavg(ctl: "Sysctl") -> Any:
        tmp = SysctlVariable.transform_struct(ctl, LOADAVG)
        scale = float(tmp["scale"])
        return (tmp["1min"] / scale, tmp["3min"] / scale, tmp["15min"] / scale)

    @staticmethod
    def transform_struct(ctl: "Sysctl", mapping: Dict) -> Dict:
        value = {}
        start = 0
        for field in mapping:
            format = TYPE[field[0]]
            offset = struct.calcsize(format)  # TODO - optimize
            bytes = ctl.value[start : start + offset]
            (value[field[1]],) = struct.unpack_from(format, ctl.value, start)
            start += offset
        return value

    @staticmethod
    def extract_struct(ctl: "Sysctl") -> Any:
        if ctl.name == "vm.vmtotal":
            mapping = VMTOTAL
        elif ctl.name == "vm.loadavg":
            return SysctlVariable.extract_loadavg(ctl)
        else:
            return ctl.value
        return SysctlVariable.transform_struct(ctl, mapping)

    @staticmethod
    def _verify_sysctl(name: str) -> sysctl.Sysctl:
        ctl = sysctl.filter(name)
        assert type(ctl) == list  # TODO: need to see if I get something else
        if len(ctl) != 1:
            raise Exception(f"{name} is not supported type")
        return ctl[0]


def instantiate_variable(name: str, params: Dict) -> Any:
    assert name

    if "sysctl" in params:
        return SysctlVariable(name, params)
    elif "syscmd" in params:
        return SyscmdVariable(name, params)
    else:
        raise Exception("Unknown variable type")
