# Copyright (c) 2021, 2022 Yoshihiro Ota <ota@j.email.ne.jp>
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE AUTHOR AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE AUTHOR OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

import logging
import os
import struct
import sys
import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from .libc import sysctl

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


class SysctlVariable(Variable):
    """
    A user defines a variable with its "name" and sysctl name for its value.
    """

    def __init__(self, name: str, params: Dict):
        super().__init__(name, params)

        self._sysctl_name = params["sysctl"]
        self._sysctl = sysctl.Sysctl(self._sysctl_name)
        self._last_value = self._value = self._sysctl.value

    def _fetch_value(self) -> Any:
        return self._sysctl.value


def instantiate_variable(name: str, params: Dict) -> Any:
    assert name

    if "sysctl" in params:
        return SysctlVariable(name, params)
    elif "syscmd" in params:
        return SyscmdVariable(name, params)
    else:
        raise Exception("Unknown variable type")
