from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from core.mixins import UserScopedMixin
from core.modules.organisations.models import Project
from core.utils import is_owner_or_admin

from .authentication import ApiKeyAuthentication
from .models import ApiKey
from .pagination import ApiKeyCursorPagination
from .permissions import HasApiKey, HasScope
from .serializers import ApiKeySerializer
from .services import create_api_key, revoke_api_key


class ApiKeyViewSet(UserScopedMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = ApiKeySerializer
    pagination_class = ApiKeyCursorPagination
    queryset = ApiKey.objects.all()  # UserScopedMixin narrows this to the user's orgs

    def get_queryset(self):
        return super().get_queryset().filter(project_id=self.kwargs["project_id"])

    def create(self, request, project_id=None):
        project = get_object_or_404(
            Project.objects.for_user(request.user), pk=project_id
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

    def revoke_key(self, request, project_id=None, key_id=None):
        project = get_object_or_404(
            Project.objects.for_user(request.user), pk=project_id
        )
        if not is_owner_or_admin(request.user, project):
            raise PermissionDenied("Only owners and admins can revoke API keys.")
        api_key = get_object_or_404(self.get_queryset(), project=project, id=key_id)
        revoke_api_key(api_key)
        return Response(ApiKeySerializer(api_key).data, status=status.HTTP_200_OK)

class WhoAmIView(APIView):
    authentication_classes = [ApiKeyAuthentication]
    permission_classes = [HasApiKey, HasScope]
    required_scope = "read"

    def get(self, request):
        key = request.auth
        return Response({"project_id": key.project_id, "key_name": key.name, "prefix": key.prefix})