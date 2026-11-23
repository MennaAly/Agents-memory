from core.queryset import TenantQuerySet


class ApiKeyQuerySet(TenantQuerySet):
    user_path = "project__organisation__memberships__user"
    project_path = "project"
