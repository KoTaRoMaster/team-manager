from typing import Union

from pydantic import EmailStr


class PasswordResetError(Exception):
    def __init__(self, message: str):
        self.message = message


class RegisterError(Exception):
    def __init__(self, message: str):
        self.message = message


class LoginError(Exception):
    def __init__(self, message: str):
        self.message = message


class NotFoundError(Exception):
    def __init__(self, entity: str, entity_data: Union[int, str | EmailStr]):
        self.entity = entity
        if isinstance(entity_data, int):
            self.entity_data = f"id={entity_data}"
        else:
            self.entity_data = f"email={entity_data}"


class DuplicateError(Exception):
    def __init__(self, field: str, value: str | EmailStr):
        self.field = field
        self.value = value


class DateValidationError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
