from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_401_UNAUTHORIZED


class InvalidCredentialsError(HTTPException):
    status_code = HTTP_401_UNAUTHORIZED
    detail = "Invalid email or password"
