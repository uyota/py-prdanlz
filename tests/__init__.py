import subprocess

OS_VERSION = subprocess.check_output(["/sbin/sysctl", "-n", "kern.osrelease"]).decode()
OS_VERSION = float(OS_VERSION[: OS_VERSION.find("-")])
