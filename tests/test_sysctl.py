import pytest

import sysctl
from . import EXAMPLES


@pytest.mark.parametrize("field", EXAMPLES)
def test_sysctl_examples(field):

    # Not supported by the library
    if field[0] in ["CTLTYPE_U8", "CTLTYPE_U16"]:
        return

    v = sysctl.filter(field[1])[0]
    print(field[0], v.type, v.value)
    assert v.value != 0
