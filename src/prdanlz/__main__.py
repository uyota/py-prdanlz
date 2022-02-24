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
        default=-1,
        help="positive number to specify interval in second to re-evaluate rules",
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
        "--verify",
        dest="verify",
        action="store_true",
        help="semi-dry run to verify input configuration - fetch and evaluate all but do not execute escalation. SyntaxError indicates error in expressions, NameError indicates wrong variable name",
    )
    parser.set_defaults(verify=False)

    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="use debug level logging",
    )
    parser.set_defaults(debug=False)

    return parser.parse_args()


def analyze(args) -> None:
    if args.verify:
        logging.basicConfig(
            stream=sys.stdout,
            level=logging.DEBUG,
            format="%(message)s",
            datefmt=args.logdateformat,
        )
    elif args.log:
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
            counts = m.load_json(setting)
            logger.info(f"Loaded from '{file.name}'")
            logger.info(f"Loaded {counts[0]} constants")
            logger.info(f"Loaded {counts[1]} variables")
            logger.info(f"Loaded {counts[2]} derivatives")
            logger.info(f"Loaded {counts[3]} incidents")
    if args.verify:
        m.verify()
    else:
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
