from core.modules.organisations.models import Member


def is_owner_or_admin(user, project):
    return Member.objects.filter(
        user=user,
        organisation=project.organisation,
        role__in=[Member.Role.OWNER, Member.Role.ADMIN],
    ).exists()
