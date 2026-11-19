from django.urls import path

from .views import ApiKeyViewSet

urlpatterns = [
    path("api/v1/projects/<int:project_id>/keys/", ApiKeyViewSet.as_view({"post": "create"}))
]