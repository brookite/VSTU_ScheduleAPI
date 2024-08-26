from rest_framework.renderers import JSONRenderer
from rest_framework.exceptions import (
    ValidationError,
    NotAuthenticated,
    PermissionDenied,
    AuthenticationFailed,
)
from rest_framework.views import exception_handler

from api.exceptions import ScheduleAPIException


class ResponseJSONRenderer(JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if renderer_context and renderer_context.get("response", None):
            response = renderer_context["response"]
            if response.status_code >= 400:
                return super().render(data, accepted_media_type, renderer_context)

        response_data = {
            "type": "response",
            "items": data if isinstance(data, list) else [data],
        }

        return super().render(response_data, accepted_media_type, renderer_context)


def exception_response_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        # Определяем тип ошибки и сообщение
        error_code = map_exception_to_errcode(exc)
        response.data = {
            "type": "error",
            "message": response.data.get("detail", "Произошла неизвестная ошибка"),
            "error_code": error_code,
        }
        if isinstance(exc, ScheduleAPIException):
            response.status_code = exc.http_code

    return response


def map_exception_to_errcode(exception):
    if isinstance(exception, ScheduleAPIException):
        return exception.internal_error_code
    elif isinstance(exception, ValidationError):
        return 1
    elif isinstance(exception, NotAuthenticated | PermissionDenied):
        return 2
    elif isinstance(exception, AuthenticationFailed):
        return 3
    elif isinstance(exception, NotImplementedError):
        return 4
    else:
        return 0
