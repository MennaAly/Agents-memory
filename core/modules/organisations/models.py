from django.conf import settings
from django.db import models


class Organisation(models.Model):
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="Member",
        related_name="organisations",
    )

    def __str__(self):
        return self.name


class Member(models.Model):
    class Role(models.TextChoices):
        OWNER = "owner", "Owner"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships"
    )
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="memberships"
    )
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organisation"], name="unique_member_per_organisation"
            ),
        ]

    def __str__(self):
        return f"{self.user} in {self.organisation} ({self.role})"


class Project(models.Model):
    organisation = models.ForeignKey(
        Organisation, on_delete=models.CASCADE, related_name="projects"
    )
    name = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organisation", "name"], name="unique_project_name_per_organisation"
            ),
        ]

    def __str__(self):
        return self.name


class EndUser(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="end_users")
    external_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "external_id"], name="unique_external_id_per_project"
            ),
        ]

    def __str__(self):
        return self.external_id
