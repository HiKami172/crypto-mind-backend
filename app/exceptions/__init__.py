from loguru import logger
from typing import Callable

from fastapi import HTTPException


class BaseHTTPException(HTTPException):
    """
    Base class for all custom exceptions.
    *_pattern is a tuple with a message and arguments to format it. Example: ('{0} not found!', 'class_name')
    """

    status_code: int = 400
    message_pattern: tuple[str, ...] | None = None

    log_level: str | None = 'debug'
    log_message_pattern: tuple | None = None

    def __init__(self, detail: str | dict = None, headers: dict[str, str] | None = None, **kwargs) -> None:
        if kwargs:
            for key, value in kwargs.items():
                setattr(self, key, value)
        self.detail = detail

        if self.message_pattern:
            message, *args = self.message_pattern
            args = [getattr(self, arg) for arg in args]
            detail = message.format(*args)

        if self.log_level in ('debug', 'info', 'warning', 'error', 'critical'):
            logger.name = self.__class__.__name__
            logger_method: Callable = getattr(logger, self.log_level)

            if self.log_message_pattern:
                log_message, *args = self.log_message_pattern
                args = [getattr(self, arg) for arg in args]
            else:
                log_message = detail
                args = []
            logger_method(log_message, *args)

        super().__init__(status_code=self.status_code, detail=[{"msg": detail}], headers=headers)
