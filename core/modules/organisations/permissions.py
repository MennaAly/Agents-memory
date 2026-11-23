from rest_framework import permissions

from .models import Member


class ProjectRolePermission(permissions.BasePermission): 
    """
    - list / retrieve: any authenticated user (UserScopedMixin filters list)
    - create / update / delete : OWNER or ADMIN
    """
    def has_permission(self, request, view):
        if not (request.user and request.user.is_authenticated):
            return False
        if view.action == "create":
            return Member.objects.filter(
                user=request.user,
                organisation_id=view.kwargs["org_id"],
                role__in=[Member.Role.OWNER, Member.Role.ADMIN],
            ).exists()

        return True
    
    def has_object_permission(self, request, view, project):
        membership = project.organisation.memberships.filter(user=request.user).first()
        if not membership:
            return False

        if view.action == "retrieve":
            return True
            
        if view.action in ("destroy", "update", "partial_update"):
            return membership.role in (Member.Role.OWNER, Member.Role.ADMIN)

        return False