from http import HTTPStatus

from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.views import exception_handler


class Conflict(APIException):
    """409: the request clashes with the current state (e.g. a unique rule in the DB)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "This conflicts with an existing resource."
    default_code = "conflict"


def problem_details_handler(exc, context):
    """Turn every DRF error into Problem Details (RFC 9457).

    {
      "type": "about:blank",
      "title": "Bad Request",
      "status": 400,
      "detail": "Invalid input.",
      "instance": "/api/v1/organisations/1/projects/",
      "errors": {"name": ["This field is required."]}   # only for validation errors
    }
    """
    response = exception_handler(exc, context)  # DRF's default: builds the response
    if response is None:
        return None  # not an API error (a real bug): let Django return a 500

    problem = {
        "type": "about:blank",
        "title": HTTPStatus(response.status_code).phrase,
        "status": response.status_code,
    }
    if isinstance(exc, ValidationError):
        problem["detail"] = "Invalid input."
        problem["errors"] = response.data  # field -> list of messages
    else:
        problem["detail"] = str(exc.detail) if hasattr(exc, "detail") else problem["title"]

    request = context.get("request")
    if request is not None:
        problem["instance"] = request.path

    response.data = problem
    response.content_type = "application/problem+json"
    return response
