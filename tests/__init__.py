import subprocess
import typing


def syscall(args: typing.List[str]) -> str:
    return subprocess.check_output(args).decode().strip()


OS_VERSION = syscall(["/sbin/sysctl", "-n", "kern.osrelease"])
OS_VERSION = float(OS_VERSION[: OS_VERSION.find("-")])
