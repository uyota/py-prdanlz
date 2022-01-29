import copy
import logging
import signal
import threading
from typing import Dict, Optional, Set

from . import Incident, instantiate_variable, Variable

logger = logging.getLogger(__name__)


class Monitor:
    def __init__(self, interval: Optional[float] = None):
        self._interval = interval
        self._constants: Set[Variable] = set()
        self._variables: Set[Variable] = set()
        self._derivatives: Dict[str, str] = {}
        self._incidents: Set[Incident] = set()
        self._locals: Dict[str, Any] = {}
        self._running: Optional[Event] = None

        if self._interval:
            signal.signal(signal.SIGINT, self.exit)
            signal.signal(signal.SIGTERM, self.exit)
            logger.info(f"Monitoring is set for {interval} seconds.")

    def exit(self, *args):
        logger.info(f"Exiting")
        self._running.set()

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

        return self._parse_variables(json, self._variables)

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
        for v in self._constants:
            self._locals[v.name] = v.value
            logger.info(f"Constant '{v.name}' holds {v.value}")

        if self._interval:
            thread: threading.Thread = None
            self._running = threading.Event()
            while not self._running.wait(self._interval):
                if thread:
                    thread.join()
                if not self._running.is_set():
                    thread = threading.Thread(target=self.fetch_and_evaluate)
                    thread.start()
        else:
            self.fetch_and_evaluate()

    def fetch_and_evaluate(self) -> None:
        locals = copy.deepcopy(self._locals)
        for v in self._variables:
            value = v.new_value()
            last_value = v.last_value
            locals[v.name] = value
            logger.info(f"'{v.name}' is loaded and holds {value}")
            locals["last_" + v.name] = last_value
            logger.info(f"'last_{v.name}' is updated and holds '{last_value}'")
        logger.debug("Reloaded all variables")

        for v, expr in self._derivatives.items():
            last_value = locals.get(v, None)
            if last_value is not None:
                locals["last_" + v] = last_value
                logger.info(f"'last_{v}' is updated and holds '{last_value}'")
            expr = eval(f'f"{expr}"', {"__builtins__": {}}, locals)
            logger.debug(f"Resolved derivative={v} to expression='{expr}'")
            value = eval(expr, {"__builtins__": {}}, locals)
            locals[v] = value
            logger.info(f"'{v}' is calculated and holds '{value}'")
        logger.debug("Reloaded all derivatives")

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
