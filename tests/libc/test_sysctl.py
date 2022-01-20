import pytest

import copy
import platform

import prdanlz.libc.sysctl as sysctl
from .. import fixture_sysctl


def test_sysctl_name2oid():
    # GIVEN
    # WHEN
    mib = sysctl.name2oid("vm.kvm_size")

    # THEN
    assert mib is not None
    assert type(mib) == list
    assert mib == [2, 2147481691]  # system specific


@pytest.mark.parametrize("name,expected", fixture_sysctl.OPAQUES)
def test_sysctl_oidfmt(name, expected):
    # GIVEN
    mib = sysctl.name2oid(name)

    # WHEN
    fmt = sysctl.oidfmt(mib)

    # THEN
    assert fmt[1] == expected


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
def test_Sysctls(name, ctltype):
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
