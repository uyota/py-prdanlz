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

    def __init__(self, name: str, typename: str, params: Dict):
        assert name
        if params.get("type", None) != typename:
            raise TypeError(f"Not {typename} type")
        if params.get(typename, None) is None:
            raise TypeError(f"Incomplete {typename} type specification")
        self._name = name
        self._value = None
        self._depth = params.get("depth", None) or params.get("history", 0)
        if self._depth < 0:
            self._depth = 0
        if self._depth != 0:
            self._hist = list()
        else:
            self._hist = None

    def __hash__(self):
        return hash(self._name)

    def __eq__(self, other) -> bool:
        return self._name == other._name

    def __repr__(self) -> Any:
        return str(self.value)

    def __getitem__(self, key) -> Any:
        # if hasattr(self, '__dict__'):
        if self._hist is not None:
            try:
                return self._hist[key]
            except IndexError:
                raise
        else:
            return self.value[key]

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> Any:
        return self._value

    @property
    def last_value(self) -> Any:
        if len(self._hist) > 0:
            return self._hist[-1]
        return None

    @property
    def oldest_value(self) -> Any:
        if len(self._hist) > 0:
            return self._hist[0]
        return None

    def new_value(self) -> Any:
        if self._value is not None:
            if self._hist is not None:
                self._hist.append(self._value)
                while len(self._hist) > self._depth:
                    self._hist.pop(0)
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
        super().__init__(name, "syscmd", params)

        self._cmd = params["syscmd"]
        self._value = self._fetch_value()

    def _fetch_value(self) -> Any:
        return os.popen(self._cmd).read().strip()


class SysctlVariable(Variable):
    """
    A user defines a variable with its "name" and sysctl name for its value.
    """

    def __init__(self, name: str, params: Dict):
        super().__init__(name, "sysctl", params)

        self._sysctl_name = params["sysctl"]
        self._sysctl = sysctl.Sysctl(self._sysctl_name)
        self._value = self._sysctl.value

    def _fetch_value(self) -> Any:
        return self._sysctl.value


def instantiate_variable(name: str, params: Dict) -> Any:
    assert name

    type = params.get("type", None)
    if type == "sysctl":
        return SysctlVariable(name, params)
    elif type == "syscmd":
        return SyscmdVariable(name, params)
    else:
        raise TypeError("Unknown variable type")
