import pytest

from freebsd_sysctl import Sysctl
from . import EXAMPLES


@pytest.mark.parametrize("field", EXAMPLES)
def test_freebsd_sysctl_examples(field):

    # Not supported by the library
    if field[0] in ["CTLTYPE_U8", "CTLTYPE_UINT", "CTLTYPE_ULONG", "CTLTYPE_LONG"]:
        return

    v = Sysctl(field[1])
    assert v.value != 0
