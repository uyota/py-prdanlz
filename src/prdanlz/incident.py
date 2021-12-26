import os
import logging
from typing import Dict

import sysctl

logger = logging.getLogger(__name__)


def _clone_with_privitives(input: Dict) -> Dict:
    return {
        key: value for key, value in input.items() if type(value) in [str, int, float]
    }


class Incident:
    class Level:
        def __init__(
            self,
            level: str,
            params: Dict,
            fallback: Dict = {},
        ):
            assert level
            self._level = level
            self._vars: Dict = _clone_with_privitives(params)
            self._vars["level"] = level
            for key in ["trigger", "untrigger", "escalation"]:
                if key not in params:
                    if key in fallback:
                        self._vars[key] = fallback[key]
                    else:
                        raise Exception(f"{level} '{key}' is missing")

            self._trigger: str = self._vars["trigger"]
            self._untrigger: str = self._vars["untrigger"]
            self._escalation: str = self._vars["escalation"]

            self._triggered: bool = False

        def clear(self) -> None:
            self._triggered = False

        def escalate_if_in_range(self, locals: Dict) -> bool:
            my_locals = {**locals, **self._vars}
            if eval(self._trigger, {"__builtins__": {}}, my_locals):
                if not self._triggered:
                    cmd = eval(f'f"{self._escalation}"', my_locals)
                    logger.debug(f"escalation at level={self._level} with cmd=[{cmd}]")
                    self._triggered = True
                    os.system(cmd)
                return True
            if self._triggered:
                if eval(self._untrigger, {"__builtins__": {}}, my_locals):
                    self._triggered = False
                else:
                    return True
            return False

    def __init__(self, params: Dict):
        if "description" in params:
            self._desc = params["description"]
        else:
            raise Exception("'description' is missing")

        count = 0
        self._levels = {}
        fallback = {}
        for key in ["error", "warn", "info"]:
            try:
                level = Incident.Level(key, params[key], fallback)
                self._levels[key] = level
                count += 1
                fallback = level._vars
            except Exception as e:
                self._levels[key] = None
        if count == 0:
            raise Exception(
                "One or more of 'info', 'warn' and/or 'error' must be specified"
            )
        self._vars: Dict = _clone_with_privitives(params)

    def escalated(self, locals: Dict) -> bool:
        in_range = False
        my_locals = None
        for key in ["error", "warn", "info"]:  # be explicit about ordering
            level = self._levels[key]
            if level:
                if in_range:
                    level.clear()
                else:
                    if my_locals is None:
                        my_locals = {**locals, **self._vars}
                    if level.escalate_if_in_range(my_locals):
                        in_range = True
        return in_range
