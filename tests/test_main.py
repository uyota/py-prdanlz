# Copyright (c) 2022 Yoshihiro Ota <ota@j.email.ne.jp>
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
import sys
from unittest.mock import patch

from prdanlz.__main__ import main, parse_args


@patch("sys.exit")
def test_parse_args__without_config(sys_exit, capsys):
    # GIVEN
    with patch("sys.argv", ["prdanlz"]):

        # WHEN
        args = parse_args()

    # THEN
    captured = capsys.readouterr()
    assert "-c/--config" in captured.err


@patch("prdanlz.monitor.Monitor.fetch_and_evaluate")
def test_main__without_interval(fetch_and_eval, capsys):
    # GIVEN
    with patch("sys.argv", ["prdanlz", "-c", "prdanlz.json"]):

        # WHEN
        main()

    # THEN
    captured = capsys.readouterr()
    assert captured.out == ""
    fetch_and_eval.called_once()


@patch("prdanlz.monitor.Monitor.fetch_and_evaluate")
def test_main__without_interval_with_logging(fetch_and_eval, capsys):
    # GIVEN
    with patch("sys.argv", ["prdanlz", "-c", "prdanlz.json", "-l", "/dev/null"]):

        # WHEN
        main()

    # THEN
    captured = capsys.readouterr()
    assert captured.out == ""
    fetch_and_eval.called_once()

@patch("prdanlz.monitor.Monitor.start")
def test_main__verify(start):
    # GIVEN
    with patch("sys.argv", ["prdanlz", "-c", "prdanlz.json", "--verify"]):

        # WHEN
        main()

    # THEN
    start.not_called()
    # Testing with capsys is more desirable but doesn't seem to capture stdout via logger
    # captured = capsys.readouterr()
    # assert "Resolved" in captured.out
