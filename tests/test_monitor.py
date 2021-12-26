import pytest
import copy

from prdanlz import Monitor

VARIABLE = {"ncpu": {"sysctl": "hw.ncpu"}}
VARIABLES = {"ncpu": {"sysctl": "hw.ncpu"}, "ostype": {"sysctl": "kern.ostype"}}


def test_monitor_add_1_variable():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_variables(VARIABLE)

    # THEN
    assert count == 1


def test_monitor_add_2_variables():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_variables(VARIABLES)

    # THEN
    assert count == 2


def test_monitor_add_same_variables():
    # GIVEN
    m = Monitor()
    count = m.add_variables(VARIABLES)

    # WHEN
    with pytest.raises(Exception) as e:
        count = m.add_variables(VARIABLES)

        # THEN
        assert e
