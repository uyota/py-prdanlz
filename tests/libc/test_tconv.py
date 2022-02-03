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

import copy
import platform

import prdanlz.libc.tconv as tconv

from .. import fixture_sysctl


def test_tconv_byte():
    # GIVEN
    nconv = tconv.byte

    # WHEN
    v = nconv.c2p(fixture_sysctl.BYTE)

    # THEN
    assert v == fixture_sysctl.BYTE

    # WHEN & THEN - the size of these types are not zero
    assert nconv.size == 0


@pytest.mark.parametrize(
    "nconv,offset,expected",
    [
        (tconv.int, 4, -19088744),
        (tconv.uint, 4, 4275878552),
        (tconv.int8, 7, -2),
        (tconv.uint8, 7, 254),
        (tconv.int16, 6, -292),
        (tconv.uint16, 6, 65244),
        (tconv.int32, 4, -19088744),
        (tconv.uint32, 4, 4275878552),
        (tconv.int64, 0, -81985529216486896),
        (tconv.uint64, 0, 18364758544493064720),
    ],
)
def test_tconv_natives(nconv, offset, expected):
    # GIVEN
    # WHEN
    v = nconv.c2p(fixture_sysctl.BYTE, offset)

    # THEN
    assert v == expected

    # WHEN & THEN - the size of these types are not zero
    assert nconv.size != 0


@pytest.mark.parametrize(
    "nconv,expected32,expected64",
    [
        (tconv.long, -19088744, -81985529216486896),
        (tconv.ulong, 4275878552, 18364758544493064720),
    ],
)
def test_tconv_longs(nconv, expected32, expected64):
    # GIVEN
    if platform.architecture()[0] == "32bit":
        offset = 4
        expected = expected32
    else:
        offset = 0
        expected = expected64

    # WHEN
    v = nconv.c2p(fixture_sysctl.BYTE, offset)

    # THEN
    assert v == expected

    # WHEN & THEN - the size of longs are not zero
    assert nconv.size != 0


def test_tconv_cstring():
    # GIVEN
    input = b"FEDCBA9876543210\x00"

    # WHEN
    v = tconv.cstr.c2p(input)

    # THEN
    assert v == "FEDCBA9876543210"

    # WHEN & THEN - the size returned is 0
    assert tconv.cstr.size == 0


def test_tconv_cstring__offset():
    # GIVEN
    input = b"FEDCBA9876543210\x00"

    # WHEN
    v = tconv.cstr.c2p(input, 8)

    # THEN
    assert v == "76543210"


def test_tconv_cstring__off_offset():
    # GIVEN
    input = b"123"

    # WHEN
    v = tconv.cstr.c2p(input, 10)

    # THEN
    assert v == ""
import pytest

import copy
import platform

import prdanlz.libc.tconv as tconv

from .. import fixture_sysctl


def test_tconv_byte():
    # GIVEN
    nconv = tconv.byte

    # WHEN
    v = nconv.c2p(fixture_sysctl.BYTE)

    # THEN
    assert v == fixture_sysctl.BYTE

    # WHEN & THEN - the size of these types are not zero
    assert nconv.size == 0


@pytest.mark.parametrize(
    "nconv,offset,expected",
    [
        (tconv.int, 4, -19088744),
        (tconv.uint, 4, 4275878552),
        (tconv.int8, 7, -2),
        (tconv.uint8, 7, 254),
        (tconv.int16, 6, -292),
        (tconv.uint16, 6, 65244),
        (tconv.int32, 4, -19088744),
        (tconv.uint32, 4, 4275878552),
        (tconv.int64, 0, -81985529216486896),
        (tconv.uint64, 0, 18364758544493064720),
    ],
)
def test_tconv_natives(nconv, offset, expected):
    # GIVEN
    # WHEN
    v = nconv.c2p(fixture_sysctl.BYTE, offset)

    # THEN
    assert v == expected

    # WHEN & THEN - the size of these types are not zero
    assert nconv.size != 0


@pytest.mark.parametrize(
    "nconv,expected32,expected64",
    [
        (tconv.long, -19088744, -81985529216486896),
        (tconv.ulong, 4275878552, 18364758544493064720),
    ],
)
def test_tconv_longs(nconv, expected32, expected64):
    # GIVEN
    if platform.architecture()[0] == "32bit":
        offset = 4
        expected = expected32
    else:
        offset = 0
        expected = expected64

    # WHEN
    v = nconv.c2p(fixture_sysctl.BYTE, offset)

    # THEN
    assert v == expected

    # WHEN & THEN - the size of longs are not zero
    assert nconv.size != 0


def test_tconv_cstring():
    # GIVEN
    input = b"FEDCBA9876543210\x00"

    # WHEN
    v = tconv.cstr.c2p(input)

    # THEN
    assert v == "FEDCBA9876543210"

    # WHEN & THEN - the size returned is 0
    assert tconv.cstr.size == 0


def test_tconv_cstring__offset():
    # GIVEN
    input = b"FEDCBA9876543210\x00"

    # WHEN
    v = tconv.cstr.c2p(input, 8)

    # THEN
    assert v == "76543210"


def test_tconv_cstring__off_offset():
    # GIVEN
    input = b"123"

    # WHEN
    v = tconv.cstr.c2p(input, 10)

    # THEN
    assert v == ""
