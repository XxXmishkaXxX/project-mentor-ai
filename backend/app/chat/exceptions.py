from litestar.exceptions import HTTPException
from litestar.status_codes import (
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_500_INTERNAL_SERVER_ERROR,
)


class ChatNotFoundError(HTTPException):
    status_code = HTTP_404_NOT_FOUND
    detail = "Chat not found"


class ChatAccessDeniedError(HTTPException):
    status_code = HTTP_403_FORBIDDEN
    detail = "Access to this chat is denied"


class MessagePersistError(HTTPException):
    status_code = HTTP_500_INTERNAL_SERVER_ERROR
    detail = "Failed to save message"
