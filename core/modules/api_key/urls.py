from django.urls import path

from .views import ApiKeyViewSet, WhoAmIView

urlpatterns = [
    path("api/v1/projects/<int:project_id>/keys/",ApiKeyViewSet.as_view({"post": "create"}),name="api-key-create"),
    path("api/v1/projects/<int:project_id>/keys/<int:key_id>/revoke/",ApiKeyViewSet.as_view({"post": "revoke_key"}),name="api-key-revoke"),
    path("api/v1/whoami/", WhoAmIView.as_view(), name="whoami"),
]
