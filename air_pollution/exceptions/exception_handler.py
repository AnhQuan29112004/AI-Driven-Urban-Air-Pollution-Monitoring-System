from rest_framework.views import exception_handler as drf_exception_handler
from rest_framework.response import Response
from constants.error_codes import ErrorCodes
from .exceptions import AppException
import traceback

def custom_exception_handler(exc, context):
    if isinstance(exc, AppException):
        return Response(exc.get_full_details(), status=exc.status_code)
    response = drf_exception_handler(exc, context)
    if response is not None:
        error_code = ErrorCodes.get_error(exc.__class__.__name__)
        if error_code == ErrorCodes.UNKNOWN_ERROR:
            error_code = (response.status_code, str(exc), response.status_code)

        return Response(
            {
                "type": "error",
                "code": error_code[0],
                "message": error_code[1],
            },
            status=error_code[2],
        )

    if response is None:
        print("Unhandled exception:", traceback.format_exc())  # 👈 debug lỗi 500
        return Response({'detail': 'Internal server error'}, status=500)
    return response

    # return Response(
    #     {
    #         "type": "error",
    #         "code": ErrorCodes.UNKNOWN_ERROR[0],
    #         "message": ErrorCodes.UNKNOWN_ERROR[1],
    #     },
    #     status=ErrorCodes.UNKNOWN_ERROR[2],
    # )
