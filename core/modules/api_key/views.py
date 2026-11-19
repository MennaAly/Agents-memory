from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from core.modules.organisations.models import Project
from core.utils import is_owner_or_admin

from .models import ApiKey
from .serializers import ApiKeySerializer
from .services import create_api_key


class ApiKeyViewSet(mixins.CreateModelMixin,viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ApiKeySerializer

    def get_queryset(self):
        if self.action == "create":
            return ApiKey.objects.all()
        if self.action == "revoke_key":
            return ApiKey.objects.filter(created_by=self.request.user)

    def create(self, request, project_id=None):
        project = get_object_or_404(
            Project, pk=project_id, organisation__memberships__user=request.user
        )
        if not is_owner_or_admin(request.user, project):
            raise PermissionDenied("Only owners and admins can create API keys.")
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        valid_api_key_req_data = serializer.validated_data
        api_key, full_key = create_api_key(
            project,
            self.request.user,
            valid_api_key_req_data["name"],
            valid_api_key_req_data.get("can_read", True),
            valid_api_key_req_data.get("can_write", False),
            valid_api_key_req_data.get("can_delete", False),
            expires_at=valid_api_key_req_data.get("expires_at", None),
        )
        response_data = ApiKeySerializer(api_key).data
        response_data["key"] = full_key
        return Response(
            response_data,
            status=status.HTTP_201_CREATED
        )

