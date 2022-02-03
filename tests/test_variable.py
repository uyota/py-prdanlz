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

from prdanlz import Variable, SyscmdVariable, SysctlVariable


def test_syscmd__ls_tmp():
    # GIVEN
    ls = {"syscmd": "ls -d /tmp"}

    # WHEN
    v = SyscmdVariable("ls", ls)

    # THEN
    assert v.value == "/tmp"


def test_syscmd__ls_dev_x():
    # GIVEN
    ls = {"syscmd": "ls -d /dev/x"}

    # WHEN
    v = SyscmdVariable("ls", ls)

    # THEN
    assert v.value == ""  # stdout is empty


def test_syscmd__ls_bad_option():
    # GIVEN
    ls = {"syscmd": "ls -% /tmp"}

    # WHEN
    v = SyscmdVariable("ls", ls)

    # THEN
    assert v.value == ""  # stdout is empty


VARIABLE_JSON = {
    "sysctl": "hw.ncpu",
}


@pytest.mark.parametrize("field", ["sysctl"])
def test_variable_missing_field(field):
    # GIVEN
    variable_dict = copy.deepcopy(VARIABLE_JSON)
    del variable_dict[field]

    # WHEN
    with pytest.raises(Exception) as e:
        v = Variable("hw__ncpu", variable_dict)

        # THEN
        assert e


def test_variable():
    # GIVEN

    # WHEN
    with pytest.raises(Exception) as e:
        v = Variable("hw__ncpu", VARIABLE_JSON)

        # THEN
        assert e is None
        assert v.value() != 0
        assert v.last_value() != 0
        assert v.new_value() != 0
