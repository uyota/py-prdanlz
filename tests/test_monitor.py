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
import threading
import time

from prdanlz import Monitor

VARIABLE = {"ncpu": {"type": "sysctl", "sysctl": "hw.ncpu"}}
VARIABLES = {
    "ncpu": {"type": "sysctl", "sysctl": "hw.ncpu"},
    "ostype": {"type": "sysctl", "sysctl": "kern.ostype"},
}
DERIVATIVE = {"expr": "1 + 1"}
DERIVATIVES = {"expr": "1 + 1", "eval": "2 * 3 + 1 "}
CHECK_INCIDENT = {
    "description": "number of CPUs",
    "info": {
        "trigger": "{ncpu} <= 4",
        "untrigger": "{ncpu} > 5",
        "escalation": "echo '{description} is {ncpu}'",
    },
}
INCIDENT = {"check": CHECK_INCIDENT}
INCIDENTS = {"check1": CHECK_INCIDENT, "check2": CHECK_INCIDENT}


JSON_ALL = {
    "constants": VARIABLE,
    "variables": {"kmem": {"type": "sysctl", "sysctl": "vm.kmem_size"}},
    "derivatives": DERIVATIVE,
    "incidents": INCIDENT,
}


def test_monitor():
    # GIVEN & WHEN
    m = Monitor()

    # THEN
    assert m


def test_monitor__with_interval():
    # GIVEN & WHEN
    m = Monitor(3)

    # THEN
    assert m


def test_monitor__exit():
    # GIVEN
    m = Monitor(3)

    # GIVEN & WHEN
    m.exit()

    # THEN
    assert m


def test_monitor__add_1_variable():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_variables(VARIABLE)

    # THEN
    assert count == 1


def test_monitor__add_2_variables():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_variables(VARIABLES)

    # THEN
    assert count == 2


def test_monitor__add_same_variables():
    # GIVEN
    m = Monitor()
    count = m.add_variables(VARIABLES)

    # WHEN
    with pytest.raises(Exception) as e:
        count = m.add_variables(VARIABLES)

        # THEN
        assert e


def test_monitor__add_1_constant():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_constants(VARIABLE)

    # THEN
    assert count == 1


def test_monitor__add_2_constants():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_constants(VARIABLES)

    # THEN
    assert count == 2


def test_monitor__add_same_constants():
    # GIVEN
    m = Monitor()
    count = m.add_constants(VARIABLES)

    # WHEN
    with pytest.raises(Exception) as e:
        count = m.add_constants(DERIVATIVES)

        # THEN
        assert e


def test_monitor__add_1_derivative():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_derivatives(DERIVATIVE)

    # THEN
    assert count == 1


def test_monitor__add_2_derivatives():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_derivatives(DERIVATIVES)

    # THEN
    assert count == 2


def test_monitor__add_same_derivatives():
    # GIVEN
    m = Monitor()
    count = m.add_derivatives(DERIVATIVES)

    # WHEN
    with pytest.raises(Exception) as e:
        count = m.add_derivatives(DERIVATIVES)

        # THEN
        assert e


def test_monitor__load_empty_json():
    # GIVEN
    m = Monitor()

    # WHEN
    counts = m.load_json({})

    # THEN
    for i in range(4):
        assert counts[i] == 0


def test_monitor__add_1_incident():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_incidents(INCIDENT)

    # THEN
    assert count == 1


def test_monitor__add_2_incidents():
    # GIVEN
    m = Monitor()

    # WHEN
    count = m.add_incidents(INCIDENTS)

    # THEN
    assert count == 2


def test_monitor__add_same_incidents():
    # GIVEN
    m = Monitor()
    count = m.add_incidents(INCIDENTS)

    # WHEN
    with pytest.raises(Exception) as e:
        count = m.add_incidents(INCIDENTS)

        # THEN
        assert e


def test_monitor__load_empty_json():
    # GIVEN
    m = Monitor()

    # WHEN
    counts = m.load_json({})

    # THEN
    for i in range(4):
        assert counts[i] == 0


def test_monitor__load_some_json():
    # GIVEN
    m = Monitor()

    # WHEN
    counts = m.load_json(JSON_ALL)

    # THEN
    for i in range(4):
        assert counts[i] == 1


def exit_monitor(m: Monitor, wait: float) -> None:
    time.sleep(wait)
    m.exit()


def test_monitor__fetch_constants():
    # GIVEN
    m = Monitor()
    m.load_json(JSON_ALL)

    # WHEN
    m.fetch_constants()

    # THEN
    assert "ncpu" in m._locals
    assert "kmem" not in m._locals
    assert "expr" not in m._locals


def test_monitor__fetch_variables():
    # GIVEN
    m = Monitor()
    m.load_json(JSON_ALL)

    # WHEN
    m.fetch_variables(m._locals)

    # THEN
    assert "ncpu" not in m._locals
    assert "kmem" in m._locals
    assert "expr" not in m._locals


def test_monitor__evaludate_derivatives():
    # GIVEN
    m = Monitor()
    m.load_json(JSON_ALL)

    # WHEN
    m.evaludate_derivatives(m._locals)

    # THEN
    assert "ncpu" not in m._locals
    assert "kmem" not in m._locals
    assert "expr" in m._locals
    assert m._locals["expr"] == 2


def test_monitor__verify_syntax_error():
    # GIVEN - missing closing bracket
    json = copy.deepcopy(JSON_ALL)
    json["incidents"]["check"]["info"]["escalation"] = "echo '{description} is {ncpu'"
    m = Monitor()
    m.load_json(json)

    # WHEN & THEN
    with pytest.raises(SyntaxError) as e:
        m.verify()


def test_monitor__verify_name_error():
    # GIVEN - wrong variable name
    json = copy.deepcopy(JSON_ALL)
    json["incidents"]["check"]["info"]["escalation"] = "echo '{description} is {cpus}'"
    m = Monitor()
    m.load_json(json)

    # WHEN & THEN
    with pytest.raises(NameError) as e:
        m.verify()


def test_monitor__verify_successful():
    # GIVEN
    m = Monitor()
    m.load_json(JSON_ALL)

    # WHEN & THEN
    m.verify()


def test_monitor__interval():
    # GIVEN
    m = Monitor(0.1)
    m.load_json(JSON_ALL)

    thread = threading.Thread(target=exit_monitor, args=(m, 0.3))
    thread.start()

    # WHEN
    m.start()

    # THEN
    thread.join()
