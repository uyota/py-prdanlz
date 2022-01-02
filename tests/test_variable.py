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


def test_variable_verify_sysctl_non_existing():
    # GIVEN
    with pytest.raises(Exception) as e:

        # WHEN
        sysctl = Variable._verify_sysctl("abc.def")

        # THEN
        assert e


def test_variable_verify_sysctl_integer():
    # GIVEN & WHEN
    sysctl = SysctlVariable._verify_sysctl("hw.ncpu")

    # THEN
    assert sysctl
    assert sysctl.value != 0


def test_variable_verify_sysctl_uint32():
    # GIVEN & WHEN
    sysctl = SysctlVariable._verify_sysctl("vm.stats.vm.v_free_count")

    # THEN
    assert sysctl
    assert sysctl.value != 0


def test_variable_verify_sysctl__vm__vmtotal():
    # GIVEN
    sysctl = SysctlVariable._verify_sysctl("vm.vmtotal")

    # WHEN
    value = SysctlVariable.extract_struct(sysctl)

    # THEN
    assert sysctl
    assert len(value) != 0
    assert type(value) == dict

def test_variable_verify_sysctl__vm__loadavg():
    # GIVEN
    sysctl = SysctlVariable._verify_sysctl("vm.loadavg")

    # WHEN
    value = SysctlVariable.extract_struct(sysctl)

    # THEN
    assert sysctl
    assert len(value) == 3
    assert type(value) == tuple


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
