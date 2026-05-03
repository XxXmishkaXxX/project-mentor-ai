from litestar.exceptions import HTTPException
from litestar.status_codes import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND


class ChatNotFoundError(HTTPException):
    status_code = HTTP_404_NOT_FOUND
    detail = "Chat not found"


class ChatAccessDeniedError(HTTPException):
    status_code = HTTP_403_FORBIDDEN
    detail = "Access to this chat is denied"
