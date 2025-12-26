from rest_framework.exceptions import APIException

from constants.error_codes import ErrorCodes


class AppException(APIException):
    def __init__(self, error_code=None, detail=None, http_status=None, extra=None):

        if isinstance(error_code, str):
            code, message, default_status = ErrorCodes.get_error(error_code)
        elif isinstance(error_code, tuple):
            code, message, default_status = error_code
        else:
            code, message, default_status = ErrorCodes.UNKNOWN_ERROR

        self.code = code
        self.error_code = error_code
        self.message = detail or message
        self.status_code = http_status or default_status
        self.extra = extra or {}

        super().__init__(detail=self.message)

    def get_full_details(self):
        return {
            "type": "error",
            "code": self.code,
            "message": self.message,
        }
