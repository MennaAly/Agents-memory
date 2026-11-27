from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.exceptions import Conflict
from core.mixins import UserScopedMixin

from .models import Member, Organisation, Project
from .pagination import ProjectCursorPagination
from .permissions import ProjectRolePermission
from .serializers import OrganisationSerializer, ProjectSerializer


class OrganisationViewSet(
    UserScopedMixin, mixins.CreateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet
):
    permission_classes = [IsAuthenticated]
    # we will use UserScopedMixin to isolate tenants when we query inside the endpoints
    queryset = Organisation.objects.all() 
    serializer_class = OrganisationSerializer
   
    def perform_create(self, serializer):
        with transaction.atomic():
            organisation = serializer.save()
            Member.objects.create(
            user=self.request.user,
            organisation=organisation,
            role=Member.Role.OWNER,
        )

class ProjectViewSet(UserScopedMixin, ModelViewSet):
    permission_classes = [ProjectRolePermission]
    serializer_class = ProjectSerializer
    queryset = Project.objects.all() 
    pagination_class = ProjectCursorPagination

    def get_queryset(self):
        return super().get_queryset().filter(organisation_id=self.kwargs["org_id"])

    def perform_create(self, serializer):
        org = get_object_or_404(
            Organisation.objects.for_user(self.request.user), pk=self.kwargs["org_id"]
        )
        self._save_or_conflict(serializer, organisation=org)

    def perform_update(self, serializer):
        self._save_or_conflict(serializer)

    def _save_or_conflict(self, serializer, **kwargs):
        # validate_name catches most duplicates, but two requests at the same moment
        # can both pass it; then the DB unique constraint fails. Return 409, not 500.
        # atomic() rolls back only this block, so the request can still respond.
        try:
            with transaction.atomic():
                serializer.save(**kwargs)
        except IntegrityError:
            raise Conflict("A project with this name already exists.") from None
    