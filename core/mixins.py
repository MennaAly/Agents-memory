class UserScopedMixin:
    """Dashboard views: only rows in orgs the signed-in developer belongs to."""
    def get_queryset(self):
        return super().get_queryset().for_user(self.request.user)


class ProjectScopedMixin:
    """API-key views: only rows in the key's project."""
    def get_queryset(self):
        return super().get_queryset().for_project(self.request.auth.project)