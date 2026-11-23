from django.urls import path

from .views import OrganisationViewSet, ProjectViewSet

urlpatterns = [
    path(
        "api/v1/organisations/",
        OrganisationViewSet.as_view({"get": "list", "post": "create"}),
        name="organisation-list",
    ),
    path(
        "api/v1/organisations/<int:org_id>/projects/",
        ProjectViewSet.as_view({"get": "list", "post": "create"}),
        name="project-list",
    ),
    path(
        "api/v1/organisations/<int:org_id>/projects/<int:pk>/",
        ProjectViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy"}
        ),
        name="project-detail",
    ),
]
