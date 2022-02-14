# Copyright (c) 2022 Yoshihiro Ota <ota@j.email.ne.jp>
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
import platform

import prdanlz.libc.sysctl as sysctl
import prdanlz.libc.tconv as tconv

from .. import fixture_sysctl, syscall


def test_sysctl_name2oid():
    # GIVEN
    name = "vm.kvm_size"

    # WHEN
    mib = sysctl.name2oid(name)

    # THEN
    assert mib is not None
    assert type(mib) == list
    # assert mib == [2, 2147481691]  # this is system specific and example value


def test_pysysctlnametomib():
    # GIVEN
    name = "vm.kvm_size"

    # WHEN
    mib = sysctl.pysysctlnametomib(name)

    # THEN
    assert mib == sysctl.name2oid(name)


@pytest.mark.parametrize("name,expected", fixture_sysctl.OPAQUES)
def test_sysctl_oidfmt(name, expected):
    # GIVEN
    mib = sysctl.name2oid(name)

    # WHEN
    fmt = sysctl.oidfmt(mib)

    # THEN
    assert fmt[1] == expected
    assert mib == sysctl.pysysctlnametomib(name)


def test_sysctl_description():
    # GIVEN
    mib = sysctl.name2oid("kern.osrelease")

    # WHEN
    desc = sysctl.oiddesc(mib)

    # THEN
    assert desc == "Operating system release"


@pytest.mark.parametrize("name", [i[1] for i in fixture_sysctl.TYPES])
def test_sysctl_descriptions(name):
    # GIVEN
    mib = sysctl.name2oid(name)

    # WHEN
    desc = sysctl.oiddesc(mib)

    # THEN
    assert type(desc) == str
    assert len(desc) > 0


@pytest.mark.parametrize("name", [i[1] for i in fixture_sysctl.TYPES])
def test_sysctl_size(name):
    # GIVEN
    mib = sysctl.name2oid(name)

    # WHEN
    size = sysctl.oidsize(mib)

    # THEN
    assert type(size) == int
    assert size > 0


def test_sysctl_value():
    # GIVEN
    mib = sysctl.name2oid("kern.ostype")
    size = sysctl.oidsize(mib)

    # WHEN
    value = sysctl.oidvalue(mib, size)

    # THEN
    assert type(value) == bytes
    assert value == b"FreeBSD\x00"


@pytest.mark.parametrize("name", [i[1] for i in fixture_sysctl.TYPES])
def test_sysctl_values(name):
    # GIVEN
    mib = sysctl.name2oid(name)
    size = sysctl.oidsize(mib)

    # WHEN
    value = sysctl.oidvalue(mib, size)

    # THEN
    assert type(value) == bytes


def test_sysctlnametomib():
    # GIVEN
    name = "vm.swap_info"

    # WHEN
    mib = sysctl.pysysctlnametomib(name)

    # THEN
    assert type(mib) == list
    assert mib == sysctl.name2oid(name)


def test_Sysctl__non_existing():
    # GIVEN
    with pytest.raises(RuntimeError) as e:

        # WHEN
        sysctl.Sysctl("a.b.c")

        # THEN
        assert e


def test_Sysctl__existing():
    # GIVEN
    s = sysctl.Sysctl("kern.ostype")

    # WHEN
    value = s.value

    # THEN
    assert type(value) == str
    assert value == "FreeBSD"


@pytest.mark.parametrize("name,ctltype", [(i[1], i[2]) for i in fixture_sysctl.TYPES])
def test_Sysctl(name, ctltype):
    # GIVEN
    ctl = sysctl.Sysctl(name)

    # THEN
    assert name == ctl.name
    assert ctl._reserve() > 0

    # WHEN
    value = ctl.value

    # THEN
    if ctltype == "string":
        assert type(value) == str
    else:
        assert type(value) == int
    assert value is not None


@pytest.mark.parametrize("field", fixture_sysctl.TYPES)
def test_Sysctl__description(field):
    # GIVEN
    name = field[1]
    ctl = sysctl.Sysctl(name)

    # WHEN & THEN
    assert ctl.description != ""


@pytest.mark.parametrize("name,expected", fixture_sysctl.OPAQUES)
def test_Sysctl__fmt(name, expected):
    # GIVEN
    ctl = sysctl.Sysctl(name)

    # WHEN & THEN
    assert ctl.fmt != ""


# def test_Sysctl__node():
#    # GIVEN
#    s = sysctl.Sysctl("kern")
#
#    # WHEN
#    value = s.value
#
#    # THEN
#    assert type(value) == bytes


@pytest.mark.parametrize("field", fixture_sysctl.TYPES)
def test_Sysctl__value(field):
    # GIVEN
    name = field[1]

    # WHEN
    ctl = sysctl.Sysctl(name)
    value = ctl.value

    # THEN
    stdout = syscall(["/sbin/sysctl", "-n", name])

    if type(value) == int:
        # few sysctl change a lot in short amount of time
        assert value == pytest.approx(int(stdout), rel=0.1)
    else:
        assert str(value) == stdout


@pytest.mark.parametrize(
    "input,expected",
    [
        ([("int", "1")], [(tconv.int, "1")]),
        ([("int", "1"), ("int", "2")], [(tconv.int, "1"), (tconv.int, "2")]),
        (
            [("int", "1"), ("int", "2"), ("long", "3")],
            [(tconv.int, "1"), (tconv.int, "2"), (tconv.long, "3")],
        ),
        ([("int", ""), ("int", "2")], [(tconv.int, ""), (tconv.int, "2")]),
        ([("int", None), ("int", "2")], [(tconv.int, None), (tconv.int, "2")]),
    ],
)
def test_DictConv__optimize(input, expected):
    # GIVEN & WHEN
    result = sysctl.DictConv.optimize(input)

    # THEN
    assert result == expected


def test_DictConv__no_mapping():
    # GIVEN
    d = sysctl.DictConv(None)

    # WHEN
    value = d.c2p(fixture_sysctl.BYTE)

    # THEN
    assert value == fixture_sysctl.BYTE


@pytest.mark.parametrize(
    "input,expected",
    [
        ([("int", "1")], {"1": 1985229328}),
        ([("int", "1"), ("int", "2")], {"1": 1985229328, "2": -19088744}),
        ([("int", ""), ("int", "2")], {"2": -19088744}),
        ([("int", None), ("int", "2")], {"2": -19088744}),
    ],
)
def test_DictConv__c2p(input, expected):
    # GIVEN
    d = sysctl.DictConv(sysctl.DictConv.optimize(input))

    # WHEN
    value = d.c2p(fixture_sysctl.BYTE)

    # THEN
    assert value == expected


@pytest.mark.parametrize(
    "input,expected_fmt,expected_names",
    [
        ([("int", "1")], "i", ["1"]),
        ([("int", "1"), ("int", "2")], "ii", ["1", "2"]),
        ([("int", "1"), ("int", "2"), ("long", "3")], "iil", ["1", "2", "3"]),
    ],
)
def test_StructConv__optimize(input, expected_fmt, expected_names):
    # GIVEN & WHEN
    (fmt, names) = sysctl.StructConv.optimize(input)

    # THEN
    assert type(fmt) == str
    assert fmt == expected_fmt
    assert type(names) == list
    assert names == expected_names


def test_StructConv__optimize_throws():
    # GIVEN
    input = [("int", "1"), ("int", None)]

    # WHEN
    with pytest.raises(RuntimeError) as e:
        sysctl.StructConv.optimize(input)

    # THEN
    assert "None" in str(e)


@pytest.mark.parametrize(
    "input,expected",
    [
        ([("int", "1")], {"1": 1985229328}),
        ([("int", "1"), ("int", "2")], {"1": 1985229328, "2": -19088744}),
    ],
)
def test_StructConv__c2p(input, expected):
    # GIVEN
    d = sysctl.StructConv(sysctl.StructConv.optimize(input))

    # WHEN
    value = d.c2p(fixture_sysctl.BYTE)

    # THEN
    assert value == expected


def test_Sysctl__fmt__clockrate():
    # GIVEN
    s = sysctl.Sysctl("kern.clockrate")

    # WHEN
    value = s.value

    # THEN
    assert s
    assert len(value) == 4
    assert type(value) == dict


def test_Sysctl__fmt__loadavg():
    # GIVEN
    s = sysctl.Sysctl("vm.loadavg")

    # WHEN
    value = s.value

    # THEN
    assert s
    assert len(value) == 3
    assert type(value) == tuple


def test_Sysctl__fmt__timeval():
    # GIVEN
    s = sysctl.Sysctl("kern.boottime")

    # WHEN
    value = s.value

    # THEN
    assert s
    assert len(value) == 2
    assert type(value) == tuple
    assert len(value[0]) == 2
    assert type(value[0]) == dict
    assert type(value[1]) == str


def test_Sysctl__fmt__vmtotal():
    # GIVEN
    s = sysctl.Sysctl("vm.vmtotal")

    # WHEN
    value = s.value

    # THEN
    assert s
    assert len(value) != 0
    assert type(value) == dict


def test_Sysctl__fmt__pagesizes():
    # GIVEN
    s = sysctl.Sysctl("hw.pagesizes")

    # WHEN
    value = s.value

    # THEN
    assert s
    if "pagesizes" in s.fmt:  # FreeBSD 12.x doesn't have this type
        assert type(value) == list
        assert len(value) != 0
    else:
        assert type(value) == int
        assert value != 0


def test_Sysctl__swap_info():
    # GIVEN
    name = "vm.swap_info"
    s = sysctl.Sysctl(name)

    # WHEN
    value = s.value
    mib = sysctl.pysysctlnametomib(name)

    # THEN
    assert type(value) == list
    assert len(value) >= 1
    assert value[-1]["device"] == "Total"

    if len(value) > 1:
        swaps = syscall(["/sbin/swapctl", "-l", "-k"]).split("\n")[1:]
        for i, swap in enumerate(swaps):
            swap = swap.split()
            assert swap[0] == value[i]["device"]
            assert int(swap[1]) == value[i]["xsw_nblks"] / 1024
            assert int(swap[2]) == value[i]["xsw_used"] / 1024
