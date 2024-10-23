from fastapi import status

from app.exceptions import BaseHTTPException


class BadRequestException(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST


class NotFoundException(BaseHTTPException):
    status_code = status.HTTP_404_NOT_FOUND
    message_pattern = ('{0} not found!', 'class_name')


class EntryAlreadyExistsException(BadRequestException):
    message_pattern = ('{0} with this {1} already exists.', 'class_name', 'unique_rows')


class InvalidEventException(BadRequestException):
    message_pattern = ('Invalid event: {0}', 'event')
