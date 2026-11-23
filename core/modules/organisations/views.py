from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from core.mixins import UserScopedMixin

from .models import Member, Organisation, Project
from .permissions import ProjectRolePermission
from .serializers import OrganisationSerializer, ProjectSerializer


class OrganisationViewSet(UserScopedMixin, mixins.CreateModelMixin, mixins.ListModelMixin,viewsets.GenericViewSet):
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

    def get_queryset(self):
        return super().get_queryset().filter(organisation_id=self.kwargs["org_id"])

    def perform_create(self, serializer):
        org = get_object_or_404(
            Organisation.objects.for_user(self.request.user), pk=self.kwargs["org_id"]
        )
        serializer.save(organisation=org)
    