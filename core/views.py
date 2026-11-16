from rest_framework.response import Response
from rest_framework.views import APIView


class HealthView(APIView):
    """Liveness check. Public: no auth, no throttling."""

    authentication_classes: list = []
    permission_classes: list = []

    def get(self, request):
        return Response({"status": "ok"})
