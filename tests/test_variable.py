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

import pytest
import copy

from prdanlz import Variable, SyscmdVariable, SysctlVariable, instantiate_variable


def test_syscmd__without_type():
    # GIVEN
    ls = {"syscmd": "ls -d /tmp"}

    # WHEN
    with pytest.raises(TypeError) as e:
        v = SyscmdVariable("ls", ls)

        # THEN
    assert "Not syscmd type" in str(e)


def test_syscmd__ls_tmp():
    # GIVEN
    ls = {"type": "syscmd", "syscmd": "ls -d /tmp"}

    # WHEN
    v = SyscmdVariable("ls", ls)

    # THEN
    assert v.value == "/tmp"


def test_syscmd__ls_dev_x():
    # GIVEN
    ls = {"type": "syscmd", "syscmd": "ls -d /dev/x"}

    # WHEN
    v = SyscmdVariable("ls", ls)

    # THEN
    assert v.value == ""  # stdout is empty


def test_syscmd__ls_bad_option():
    # GIVEN
    ls = {"type": "syscmd", "syscmd": "ls -% /tmp"}

    # WHEN
    v = SyscmdVariable("ls", ls)

    # THEN
    assert v.value == ""  # stdout is empty


def test_sysctl__without_type():
    # GIVEN
    os = {"sysctl": "kern.ostype"}

    # WHEN
    with pytest.raises(TypeError) as e:
        v = SysctlVariable("os", os)

        # THEN
    assert "Not sysctl type" in str(e)


def test_sysctl__kern_ostype():
    # GIVEN
    os = {"type": "sysctl", "sysctl": "kern.ostype"}

    # WHEN
    v = SysctlVariable("os", os)

    # THEN
    assert v.value == "FreeBSD"


def test_sysctl__bad_ostype():
    # GIVEN
    os = {"type": "sysctl", "sysctl": "ostype"}

    # WHEN
    with pytest.raises(ValueError) as e:
        v = SysctlVariable("os", os)

        # THEN
        assert "Invalid sysctl name" in str(e)


SYSCTL_JSON = {"type": "sysctl", "sysctl": "hw.ncpu"}
SYSCMD_JSON = {"type": "syscmd", "syscmd": "/bin/echo ABC"}


@pytest.mark.parametrize(
    "field,expect",
    [
        ("type", "Unknown variable type"),
        ("sysctl", "Incomplete sysctl type specification"),
    ],
)
def test_variable_missing_field(field, expect):
    # GIVEN
    variable_dict = copy.deepcopy(SYSCTL_JSON)
    del variable_dict[field]

    # WHEN
    with pytest.raises(TypeError) as e:
        print(variable_dict)
        v = instantiate_variable("hw__ncpu", variable_dict)

        # THEN
    assert expect in str(e)


def test_instantiate_variable__sysctl():
    # GIVEN & WHEN
    v = instantiate_variable("hw__ncpu", SYSCTL_JSON)

    # THEN
    assert v.value != 0
    assert v.new_value() != 0


def test_instantiate_variable__syscmd():
    # GIVEN & WHEN
    v = instantiate_variable("echo", SYSCMD_JSON)

    # THEN
    assert v.value == "ABC"
    assert v.new_value() == "ABC"


def test_instantiate_variable__syscmd_over_sysctl():
    # GIVEN & WHEN
    v = instantiate_variable("which", {**SYSCTL_JSON, **SYSCMD_JSON})

    # THEN
    assert v.value == "ABC"
    assert v.new_value() == "ABC"


def test_instantiate_variable__sysctl_over_syscmd():
    # GIVEN & WHEN
    v = instantiate_variable("which", {**SYSCMD_JSON, **SYSCTL_JSON})

    # THEN
    assert v.value != "ABC"
    assert v.new_value() != "ABC"
