from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from utils.translate import translate_text


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    response.data[key] = [translate_text(str(v)) for v in value]
                else:
                    response.data[key] = translate_text(str(value))

    return response
