from datetime import date, datetime

import pytest

from leave import (
    calculate_leave_days,
    validate_leave_request,
    can_approve,
    remaining_balance,
    FACULTY_APPROVAL_LIMIT,
    HOD_APPROVAL_LIMIT,
)


# ----- Leave days (accepts both str and date) -----
def test_single_day_leave():
    assert calculate_leave_days(date(2026, 11, 2), date(2026, 11, 2)) == 1


def test_multiple_day_leave():
    assert calculate_leave_days(date(2026, 11, 2), date(2026, 11, 4)) == 3


def test_end_date_before_start_date():
    with pytest.raises(ValueError):
        calculate_leave_days(date(2026, 11, 4), date(2026, 11, 2))


def test_string_dates_also_work():
    assert calculate_leave_days("2026-11-01", "2026-11-03") == 3


# ----- Validation -----
def test_validate_requires_dates():
    with pytest.raises(ValueError):
        validate_leave_request("", "2026-11-02", "Medical appointment")


def test_validate_requires_reason():
    with pytest.raises(ValueError):
        validate_leave_request("2026-11-01", "2026-11-02", "   ")


def test_validate_accepts_good_request():
    assert validate_leave_request("2026-11-01", "2026-11-02",
                                  "Medical appointment") is True


# ----- Approval limits -----
@pytest.mark.parametrize("days,expected", [(1, True), (3, True), (4, False)])
def test_faculty_approval_limit(days, expected):
    assert can_approve("faculty", days) is expected


@pytest.mark.parametrize("days,expected", [(1, True), (10, True), (11, False)])
def test_hod_approval_limit(days, expected):
    assert can_approve("hod", days) is expected


def test_unknown_role_cannot_approve():
    assert can_approve("student", 1) is False


# ----- Balance -----
def test_remaining_balance():
    assert remaining_balance(20, 5) == 15
    assert remaining_balance(20, 25) == 0