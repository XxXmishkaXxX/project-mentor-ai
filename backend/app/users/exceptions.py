from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_404_NOT_FOUND, HTTP_409_CONFLICT


class UserAlreadyExistsError(HTTPException):
    status_code = HTTP_409_CONFLICT
    detail = "User with this email or username already exists"


class UserNotFoundError(HTTPException):
    status_code = HTTP_404_NOT_FOUND
    detail = "User not found"
