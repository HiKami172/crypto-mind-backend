from fastapi import status

from app.exceptions import BaseHTTPException


class InvalidTokenSignatureException(BaseHTTPException):
    status_code = status.HTTP_400_BAD_REQUEST
    message_pattern = ('Invalid token signature.',)


class TokenExpireException(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message_pattern = ('Token has been expired.',)


class CredentialsException(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message_pattern = ('Could not validate credentials.',)
    log_level = 'info'


class IncorrectEmailOrPassException(BaseHTTPException):
    status_code = status.HTTP_401_UNAUTHORIZED
    message_pattern = ('Incorrect email or password.',)
    log_level = 'info'


class PermissionDenied(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    log_level = 'info'


class AccountDisabledException(BaseHTTPException):
    status_code = status.HTTP_403_FORBIDDEN
    message_pattern = ('Your account is disabled.',)
    log_level = 'info'
