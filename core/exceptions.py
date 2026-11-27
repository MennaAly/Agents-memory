from rest_framework import status
from rest_framework.exceptions import APIException


class Conflict(APIException):
    """409: the request clashes with the current state (e.g. a unique rule in the DB)."""

    status_code = status.HTTP_409_CONFLICT
    default_detail = "This conflicts with an existing resource."
    default_code = "conflict"
