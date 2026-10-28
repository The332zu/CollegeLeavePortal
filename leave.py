"""Business logic for the College Leave Portal (pure Python, testable)."""
from datetime import datetime, date
FACULTY_APPROVAL_LIMIT = 3
HOD_APPROVAL_LIMIT = 10
APPROVAL_LIMITS = {"faculty": FACULTY_APPROVAL_LIMIT, "hod": HOD_APPROVAL_LIMIT}
MIN_REASON_LENGTH = 5
INITIAL_LEAVE_BALANCE = 20
def parse_date(value):
    """Accept a date, datetime, or ISO date string; return date."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return datetime.strptime(value, "%Y-%m-%d").date()
def calculate_leave_days(start_str, end_str):
    """Return inclusive number of leave days; raise on invalid range."""
    start = parse_date(start_str)
    end = parse_date(end_str)
    if end < start:
        raise ValueError("End date cannot be before start date")
    return (end - start).days + 1
def validate_leave_request(start_str, end_str, reason):
    """Raise ValueError if any field invalid; return True otherwise."""
    if not start_str or not end_str:
        raise ValueError("Start and end dates are required")
    if not reason or not reason.strip():
        raise ValueError("Reason is required")
    if len(reason.strip()) < MIN_REASON_LENGTH:
        raise ValueError(f"Reason must be at least {MIN_REASON_LENGTH} characters")
    calculate_leave_days(start_str, end_str)
    return True
def can_approve(role, days):
    """Return True if role ('faculty' or 'hod') may approve `days`."""
    limit = APPROVAL_LIMITS.get(role)
    return limit is not None and days <= limit
def remaining_balance(initial_balance, approved_days):
    if approved_days < 0:
        raise ValueError("Approved days cannot be negative")
    return max(0, initial_balance - approved_days)
