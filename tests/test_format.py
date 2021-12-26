import pytest

# @pytest.mark.version_check(min_version=38)
def test_format():
    var = "variable"
    # print(f"{var=}") # min 3.8
    print(f"var={var}")
