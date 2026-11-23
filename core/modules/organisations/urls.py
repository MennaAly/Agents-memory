from django.urls import path

from .views import OrganisationViewSet

urlpatterns = [
    path(
        "api/v1/organisations/",
        OrganisationViewSet.as_view({"get": "list", "post": "create"}),
        name="organisation-list",
    ),
]
