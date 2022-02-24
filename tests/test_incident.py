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
import itertools
from unittest import mock

from prdanlz import Incident
from prdanlz.incident import _clone_with_primitives


@pytest.mark.parametrize(
    "input,size",
    [
        ({"a": "A"}, 1),
        ({"i": 1}, 1),
        ({"f": 3.14}, 1),
        ({"l": []}, 0),
        ({"d": {}}, 0),
        ({"None": None}, 0),
    ],
)
def test_dict_clone(input, size):
    copy = _clone_with_primitives(input)
    assert len(copy) == size


LEVEL_DICT = {
    "trigger": "1 < {value}",
    "untrigger": "{value} < 0.5",
    "escalation": "echo trigger condition was [{trigger}]",
    "remediation": "N/A",
}
INCIDENT_DICT1 = {
    "description": "Check the number of CPUs",
    "error": LEVEL_DICT,
    "warn": LEVEL_DICT,
    "info": LEVEL_DICT,
}
INCIDENT_DICT2 = {
    "description": "Check the number of CPUs",
    "error": {
        "trigger": "3 < {value}",
        "untrigger": "{value} < 2.8",
        "escalation": "echo '{level} trigger condition was [{trigger}] with [value={value}]'",
    },
    "warn": {"trigger": "2 < {value}", "untrigger": "{value} < 1.8"},
    "info": {"trigger": "1 < {value}", "untrigger": "{value} < 0.8"},
}


@pytest.mark.parametrize("field", LEVEL_DICT.keys())
def test_incident_level_missing_field(field):
    # GIVEN
    level_dict = copy.deepcopy(LEVEL_DICT)
    del level_dict[field]

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident.Level(level_dict)

        # THEN
        assert e


@pytest.mark.parametrize("field", LEVEL_DICT.keys())
def test_incident_level_missing_field_filled_with_default(field):
    # GIVEN
    level_dict = copy.deepcopy(LEVEL_DICT)
    del level_dict[field]

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident.Level(level_dict, "dummy1", "dummy2")

        # THEN
        assert e


@pytest.mark.parametrize(
    "field,context",
    [
        ("trigger", "1 < {value"),
        ("untrigger", "{value < 0.5"),
        ("escalation", "echo trigger condition was [trigger}]"),
    ],
)
def test_incident_level__verify_fields(field, context):
    # GIVEN
    level_dict = copy.deepcopy(LEVEL_DICT)
    level_dict[field] = context

    # WHEN
    l = Incident.Level("test", level_dict)

    # THEN
    with pytest.raises(SyntaxError) as e:
        l.verify({"value": 11, "trigger": 22})


@pytest.mark.parametrize("field", ["description"])
def test_incident_missing_field(field):
    # GIVEN
    incident_dict = copy.deepcopy(INCIDENT_DICT1)
    del incident_dict[field]

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident("test", incident_dict)

        # THEN
        assert e


@pytest.mark.parametrize("fields", itertools.combinations(["error", "warn", "info"], 2))
def test_incident_missing_optional_fields(fields):
    # GIVEN
    incident_dict = copy.deepcopy(INCIDENT_DICT1)
    for field in fields:
        del incident_dict[field]

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident("test", incident_dict)

        # THEN
        assert e is None
        assert i


def test_incident():
    # GIVEN
    incident_dict = copy.deepcopy(INCIDENT_DICT1)

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident("test", incident_dict)

        # THEN
        assert e is None


def test_incident__verify():
    # GIVEN
    incident_dict = copy.deepcopy(INCIDENT_DICT1)
    incident_dict["info"]["escalation"] = "echo trigger condition was [trigger}]"

    # WHEN
    i = Incident("test", incident_dict)

    # THEN
    with pytest.raises(SyntaxError) as e:
        i.verify({"value": 11, "trigger": 22})


def test_incident_critial_is_not_a_level_by_default():
    # GIVEN
    incident_dict = {
        "description": "Check the number of CPUs",
        "critical": LEVEL_DICT,
    }

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident("test", incident_dict)

        # THEN
        assert e
        assert i is None


def test_incident_critial_is_a_custom_level():
    # GIVEN
    incident_dict = {
        "description": "Check the number of CPUs",
        "critical": LEVEL_DICT,
    }
    Incident.level = ["critical"]

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident("test", incident_dict)

        # THEN
        assert e is None
        assert i


def test_incident_desc_instead_of_description():
    # GIVEN
    incident_dict = copy.deepcopy(INCIDENT_DICT1)
    incident_dict["desc"] = incident_dict["description"]
    del incident_dict["description"]

    # WHEN
    with pytest.raises(Exception) as e:
        i = Incident("test", incident_dict)

        # THEN
        assert e is None


def test_incident_not_escalated():
    # GIVEN
    i = Incident("test", INCIDENT_DICT1)

    # WHEN & THEN
    assert not i.escalated({"value": 0})


def test_incident_escalated():
    # GIVEN
    i = Incident("test", INCIDENT_DICT1)

    # WHEN & THEN
    assert i.escalated({"value": 2})


@mock.patch("os.system")
def test_incident_escalating(os_system):
    # GIVEN
    i = Incident("test", INCIDENT_DICT2)

    # WHEN
    assert i.escalated({"value": 1.5})
    # THEN
    assert "info trigger condition was " in os_system.mock_calls[0][1][0]

    # WHEN
    assert i.escalated({"value": 3.5})
    # THEN
    assert "error trigger condition was " in os_system.mock_calls[1][1][0]


# 0 -> 0.5 | 1.5 | 2.5 | 3.5 -> 0.9
CASE1 = [
    (0.5, None, None),
    (1.5, "info", None),
    (2.5, "warn", None),
    (3.5, "error", None),
    (4.5, "error", None),
]


@mock.patch("os.system")
@pytest.mark.parametrize("value,expected1,expected2", CASE1)
def test_incident_escalating_from_0_x_09(os_system, value, expected1, expected2):
    # GIVEN
    i = Incident("test", INCIDENT_DICT2)
    idx = 0
    i.escalated({"value": 0})

    # WHEN
    i.escalated({"value": value})
    # THEN
    if expected1:
        assert f"{expected1} trigger condition was " in os_system.mock_calls[idx][1][0]
        idx += 1
    else:
        assert len(os_system.mock_calls) == idx

    # WHEN
    i.escalated({"value": 0.9})
    # THEN
    if expected2:
        assert f"{expected2} trigger condition was " in os_system.mock_calls[idx][1][0]
        idx += 1
    else:
        assert len(os_system.mock_calls) == idx


# 2.5 -> 0.9 | 1.9 | 2.9 | 3.9 -> 2.1
CASE2 = [
    (0.9, None, "warn"),
    (1.9, None, None),
    (2.9, None, None),
    (3.9, "error", "warn"),
    (4.9, "error", "warn"),
]


@mock.patch("os.system")
@pytest.mark.parametrize("value,expected1,expected2", CASE2)
def test_incident_escalating_from_25_x_21(os_system, value, expected1, expected2):
    # GIVEN
    i = Incident("test", INCIDENT_DICT2)
    idx = 0

    # WHEN
    i.escalated({"value": 2.5})
    # THEN
    assert f"warn trigger condition was " in os_system.mock_calls[idx][1][0]
    idx += 1

    # WHEN
    i.escalated({"value": value})
    # THEN
    if expected1:
        assert f"{expected1} trigger condition was " in os_system.mock_calls[idx][1][0]
        idx += 1
    else:
        assert len(os_system.mock_calls) == idx

    # WHEN
    i.escalated({"value": 2.1})
    # THEN
    if expected2:
        assert f"{expected2} trigger condition was " in os_system.mock_calls[idx][1][0]
        idx += 1
    else:
        assert len(os_system.mock_calls) == idx


# 2.5 -> 0.7 | 1.7 | 2.7 | 3.7 | 4.7 -> 1.9
CASE3 = [
    (0.7, None, "info"),
    (1.7, "info", None),
    (2.7, None, None),
    (3.7, "error", "info"),
    (4.7, "error", "info"),
]


@mock.patch("os.system")
@pytest.mark.parametrize("value,expected1,expected2", CASE3)
def test_incident_escalating_from_25_x_19(os_system, value, expected1, expected2):
    # GIVEN
    i = Incident("test", INCIDENT_DICT2)
    idx = 0

    # WHEN
    i.escalated({"value": 2.5})
    # THEN
    assert f"warn trigger condition was " in os_system.mock_calls[idx][1][0]
    idx += 1

    # WHEN
    i.escalated({"value": value})
    # THEN
    if expected1:
        assert f"{expected1} trigger condition was " in os_system.mock_calls[1][1][0]
        idx += 1
    else:
        assert len(os_system.mock_calls) == idx

    # WHEN
    i.escalated({"value": 1.9})
    # THEN
    if expected2:
        assert f"{expected2} trigger condition was " in os_system.mock_calls[idx][1][0]
    else:
        assert len(os_system.mock_calls) == idx
