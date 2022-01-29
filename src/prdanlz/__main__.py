import argparse
import logging
import json
import signal
import sys
import os

from . import Monitor, Incident

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        dest="config",
        type=argparse.FileType("r"),
        required=True,
        nargs="+",
        help="configuration file to specify sysctl monitoring and their actions",
    )

    parser.add_argument(
        "-i",
        "--interval",
        dest="interval",
        type=float,
        required=False,
        help="interval in second to re-evaluate rules",
    )

    parser.add_argument(
        "-l",
        "--log",
        dest="log",
        type=str,
        required=False,
        help="the name of the log file.  If not specified, logging is disabled",
    )

    parser.add_argument(
        "--log-format",
        dest="logformat",
        type=str,
        default="%(asctime)s %(levelname)s %(name)s | %(message)s",
        help="log line format",
    )

    parser.add_argument(
        "--log-dateformat",
        dest="logdateformat",
        type=str,
        default="%Y-%m-%d_%H:%M:%S",
        help="log date format",
    )

    parser.add_argument(
        "--levels",
        dest="levels",
        type=str,
        default=["error", "warn", "info"],
        nargs="+",
        help="specify custom levels",
    )

    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="use debug level logging",
    )
    parser.set_defaults(debug=False)

    return parser.parse_args()


def analyze(args):
    if args.log:
        logging.basicConfig(
            filename=args.log,
            level=logging.DEBUG if args.debug else logging.INFO,
            format=args.logformat,
            datefmt=args.logdateformat,
        )
    else:
        logging.disable(logging.CRITICAL)

    Incident.levels = args.levels
    m = Monitor(args.interval)
    for file in args.config:
        with file as json_file:
            setting = json.load(json_file)
            if "constants" in setting:
                logger.debug(f"Loading constants from '{file.name}'")
                m.add_constants(setting["constants"])
            if "variables" in setting:
                logger.debug(f"Loading variables from '{file.name}'")
                m.add_variables(setting["variables"])
            if "derivatives" in setting:
                logger.debug(f"Loading derivatives from '{file.name}'")
                m.add_derivatives(setting["derivatives"])
            if "incidents" in setting:
                logger.debug(f"Loading incidents from '{file.name}'")
                m.add_incidents(setting["incidents"])
    m.start()


def main():
    args = parse_args()
    try:
        analyze(args)
    except KeyboardInterrupt:
        try:
            signal.signal(signal.SIGINT, signal.SIG_IGN)
            sys.exit(0)
        except SystemExit:
            os._exit(0)


if __name__ == "__main__":
    main()
