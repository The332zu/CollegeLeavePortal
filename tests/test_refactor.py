import pytest
from leave import can_approve


def legacy_can_approve(role, days):
    """Original messy implementation kept here only to compare behaviour."""
    if role == "faculty":
        if days <= 3:
            return True
        else:
            return False
    else:
        if role == "hod":
            if days <= 10:
                return True
            else:
                return False
        else:
            return False


@pytest.mark.parametrize("role", ["faculty", "hod", "student", "unknown"])
@pytest.mark.parametrize("days", [1, 2, 3, 4, 9, 10, 11, 50])
def test_refactored_matches_legacy(role, days):
    assert can_approve(role, days) == legacy_can_approve(role, days)