from app.exceptions.request_exceptions import (
    BadRequestException,
    NotFoundException,
    EntryAlreadyExistsException,
    InvalidEventException,
)


def test_bad_request_exception():
    """Test BadRequestException."""
    exception = BadRequestException(detail="Bad request occurred")
    assert exception.status_code == 400
    assert exception.detail == [{"msg": "Bad request occurred"}]


def test_not_found_exception():
    """Test NotFoundException with message formatting."""
    exception = NotFoundException(class_name="User")
    assert exception.status_code == 404
    assert exception.detail == [{"msg": "User not found!"}]


def test_entry_already_exists_exception():
    """Test EntryAlreadyExistsException with message formatting."""
    exception = EntryAlreadyExistsException(class_name="User", unique_rows="email")
    assert exception.status_code == 400
    assert exception.detail == [{"msg": "User with this email already exists."}]


def test_invalid_event_exception():
    """Test InvalidEventException with message formatting."""
    exception = InvalidEventException(event="Unauthorized Access")
    assert exception.status_code == 400
    assert exception.detail == [{"msg": "Invalid event: Unauthorized Access"}]
