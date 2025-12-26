from typing import List, Optional, Union, Dict
from rest_framework.response import Response
from constants.error_codes import ErrorCodes
from constants.success_codes import SuccessCodes
from constants.status_codes import StatusCodes
from constants.warning_codes import WarningCodes


class AppResponse:
    @staticmethod
    def success(
        success_code: tuple = SuccessCodes.DEFAULT,
        data=None,
    ):
        try:
            code, message = success_code
        except (ValueError, TypeError):
            code, message = SuccessCodes.DEFAULT
        response = {
            "type": "success",
            "code": code,
            "message": message,
            "data": data,
        }
        return Response(status=StatusCodes.OK, data=response)

    def warning(
        data=None,
        success_code: tuple = WarningCodes.DEFAULT,
    ):
        try:
            code, message = success_code
        except (ValueError, TypeError):
            code, message = WarningCodes.DEFAULT
        response = {
            "type": "warning",
            "code": code,
            "message": message,
            "data": data,
        }
        return Response(status=StatusCodes.OK, data=response)

    @staticmethod
    def error(
        error_code: tuple = ErrorCodes.UNKNOWN_ERROR,
        errors: Optional[Union[str, Dict, List[Union[str, Dict]]]] = None,
        **kwargs
    ) -> Response:
        try:
            code, message, http_status = error_code
        except (ValueError, TypeError):
            code, message, http_status = ErrorCodes.UNKNOWN_ERROR

        formatted_errors = []
        if isinstance(errors, str):
            formatted_errors.append({"message": errors})
        elif isinstance(errors, dict):
            for field, field_errors in errors.items():
                if isinstance(field_errors, list):
                    for error_msg in field_errors:
                        formatted_errors.append(
                            {"field": field, "message": str(error_msg)}
                        )
                else:
                    formatted_errors.append(
                        {"field": field, "message": str(field_errors)}
                    )

        elif isinstance(errors, list):
            for error in errors:
                if isinstance(error, dict):
                    formatted_errors.append(error)
                else:
                    formatted_errors.append({"message": str(error)})

        response = {
            "type": "error",
            "code": code,
            "message": message,
            "errors": formatted_errors,
            **kwargs,
        }

        return Response(status=http_status, data=response)
