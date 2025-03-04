from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None and response.status_code in [401, 403, 405, 404]:
        response.data = {"status": False, "message": response.data["detail"]}
    elif response is not None and response.status_code == 400:
        response.data = {"status": False, "message": response.data}

    return response
