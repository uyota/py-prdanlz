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

import copy
import logging
import signal
import threading
from typing import Dict, Optional, Set, Tuple

from . import Incident, instantiate_variable, Variable

logger = logging.getLogger(__name__)


class Monitor:
    _functions = {"__builtins__": {"abs": abs, "len": len, "max": max, "min": min}}

    def __init__(self, interval: float = -1):
        self._interval = interval
        self._constants: Set[Variable] = set()
        self._variables: Set[Variable] = set()
        self._derivatives: Dict[str, str] = {}
        self._incidents: Set[Incident] = set()
        self._locals: Dict[str, Any] = {}
        self._running: Optional[Event] = None

        if self._interval > 0:
            signal.signal(signal.SIGINT, self.exit)
            signal.signal(signal.SIGTERM, self.exit)
            logger.info(f"Monitoring is set for {interval} seconds.")

    def exit(self, *args):
        logger.info(f"Exiting")
        if self._running is not None:
            self._running.set()

    def load_json(self, json: Dict) -> Tuple[int, int, int, int]:
        constants = 0
        variables = 0
        derivatives = 0
        incidents = 0
        if "constants" in json:
            logger.debug(f"Loading constants")
            constants = self.add_constants(json["constants"])
        if "variables" in json:
            logger.debug(f"Loading variables")
            variables = self.add_variables(json["variables"])
        if "derivatives" in json:
            logger.debug(f"Loading derivatives")
            derivatives = self.add_derivatives(json["derivatives"])
        if "incidents" in json:
            logger.debug(f"Loading incidents")
            incidents = self.add_incidents(json["incidents"])
        return (constants, variables, derivatives, incidents)

    def add_constants(self, json: Dict) -> int:
        return self._parse_variables(json, self._constants)

    def add_variables(self, json: Dict) -> int:
        return self._parse_variables(json, self._variables)

    def add_derivatives(self, json: Dict) -> int:
        count = 0
        for key, value in json.items():
            for container in [self._constants, self._variables, self._derivatives]:
                if key in container:
                    raise Exception(f"Variable '{key}' already exists")

            self._derivatives[key] = value
            logger.info(f"Derivative '{key}' is configured")
            count += 1
        return count

    def add_incidents(self, json: Dict) -> int:
        count = 0
        for key, json in json.items():
            incident = Incident(key, json)
            if incident in self._incidents:
                raise Exception(f"Incident '{key}' already exists")
            self._incidents.add(incident)
            logger.info(f"Incident '{incident.name}' is configured")
            count += 1
        return count

    def start(self) -> None:
        self.fetch_constants()

        self.fetch_and_evaluate()
        if self._interval > 0:
            thread: threading.Thread = None
            self._running = threading.Event()
            while not self._running.wait(self._interval):
                if thread:
                    thread.join()
                if not self._running.is_set():
                    thread = threading.Thread(target=self.fetch_and_evaluate)
                    thread.start()

    def fetch_and_evaluate(self) -> None:
        locals = copy.deepcopy(self._locals)
        try:
            self.fetch_variables(locals)
            self.evaludate_derivatives(locals)
            self.evaluate_incidents(locals)
        except IndexError:
            pass

    def fetch_constants(self) -> None:
        for v in self._constants:
            self._locals[v.name] = v.value
            logger.info(f"Constant '{v.name}' holds {v.value}")

    def fetch_variables(self, locals: Dict) -> None:
        for v in self._variables:
            v.new_value()
            locals[v.name] = v
            logger.info(f"'{v.name}' is loaded and holds {v}")
        logger.debug("Reloaded all variables")

    def evaludate_derivatives(self, locals: Dict) -> None:
        for v, expr in self._derivatives.items():
            expr = eval(f'f"{expr}"', Monitor._functions, locals)
            logger.debug(f"Resolved derivative={v} to expression='{expr}'")
            value = eval(expr, Monitor._functions, locals)
            locals[v] = value
            logger.info(f"'{v}' is calculated and holds '{value}'")
        logger.debug("Calculated all derivatives")

    def evaluate_incidents(self, locals: Dict) -> None:
        for incident in self._incidents:
            logger.debug(f"Evaluating '{incident.name}' incident")
            incident.escalated(locals)
        logger.debug("Evaluated all incidents")

    def _parse_variables(self, json: Dict, container: Set) -> int:
        count = 0
        for key, json in json.items():
            variable = instantiate_variable(key, json)
            for existing in [self._constants, self._variables, self._derivatives]:
                if variable in existing:
                    raise Exception(f"Variable '{key}' already exists")
            container.add(variable)
            logger.info(f"Variable '{variable.name}' is configured")
            count += 1
        return count

    def verify(self) -> None:
        self.fetch_constants()
        self.fetch_variables(self._locals)
        self.evaludate_derivatives(self._locals)

        for incident in self._incidents:
            incident.verify(self._locals)
