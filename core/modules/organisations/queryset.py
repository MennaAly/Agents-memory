from core.queryset import TenantQuerySet


class OrganisationQuerySet(TenantQuerySet):
    user_path = "memberships__user"


class MemberQuerySet(TenantQuerySet):
    user_path = "organisation__memberships__user"


class ProjectQuerySet(TenantQuerySet):
    user_path = "organisation__memberships__user"


class EnduserQuerySet(TenantQuerySet):
    user_path = "project__organisation__memberships__user"
    project_path = "project"
