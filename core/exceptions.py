from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


def custom_exception_handler(exception: Exception, context: dict):
    response = exception_handler(exception, context)

    if response is not None and isinstance(exception, APIException) and isinstance(response.data, dict):
        response.data["error_code"] = exception.get_codes()

    return response


class IsNotCompanyException(APIException):
    status_code = 400
    default_code = "is_not_company"
