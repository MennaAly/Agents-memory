from django.db import transaction
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from core.mixins import UserScopedMixin

from .models import Member, Organisation
from .serializers import OrganisationSerializer

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
