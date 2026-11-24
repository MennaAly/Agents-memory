from django.core.exceptions import ImproperlyConfigured
from django.db import models


class TenantQuerySet(models.QuerySet):
    user_path = None
    project_path = None

    def for_user(self, user):
        if self.user_path is None: 
            raise ImproperlyConfigured(
                    f"{self.model.__name__} has no user_path set on its QuerySet."
                )
        return self.filter(**{self.user_path: user})
    
    def for_project(self, project):
        if self.project_path is None: 
            raise ImproperlyConfigured(
                    f"{self.model.__name__} has no project_path set on its QuerySet."
                )
        return self.filter(**{self.project_path: project})

