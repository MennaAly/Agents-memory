from rest_framework.permissions import BasePermission

from core.modules.organisations.models import Member

from .models import ApiKey


class HasApiKey(BasePermission):
    message = "A valid API key is required."
    def has_permission(self, request, view):
        return isinstance(request.auth, ApiKey)

class HasScope(BasePermission):
    message = "This API key doesn't have the required scope."
    def has_permission(self, request, view):
        # Each view declares what it needs:
        # - APIView: required_scope = "read"
        # - ViewSet: required_scopes = {"list": "read", "destroy": "delete"}
        scope = getattr(view, "required_scope", None)
        if scope is None:
            action = getattr(view, "action", None)  # only viewsets have .action
            scope = getattr(view, "required_scopes", {}).get(action)
        if scope is None:
            return True
        return getattr(request.auth, f"can_{scope}", False)

class IsOrgAdmin(BasePermission):                 
    message = "Only owners and admins can do this."
    def has_object_permission(self, request, view, obj):
        return Member.objects.filter(
            user=request.user, organisation=obj.organisation, role__in=["owner", "admin"]
        ).exists()