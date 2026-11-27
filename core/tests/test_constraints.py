"""Database constraints: one test per rule.

Each test breaks a rule and expects IntegrityError. The insert runs inside
transaction.atomic() so the error only rolls back that block; without it, the
test's transaction is broken and any later query in the test fails.
"""

from datetime import timedelta

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from core.modules.api_key.models import ApiKey
from core.modules.organisations.models import EndUser, Member, Project
from core.tests.factories import (
    ApiKeyFactory,
    EndUserFactory,
    MemberFactory,
    ProjectFactory,
    UserFactory,
)

pytestmark = pytest.mark.django_db


# ---------- Member: unique (user, organisation) ----------


def test_user_cannot_join_same_org_twice():
    member = MemberFactory()

    with pytest.raises(IntegrityError), transaction.atomic():
        Member.objects.create(user=member.user, organisation=member.organisation)


def test_user_can_join_two_orgs():
    user = UserFactory()
    MemberFactory(user=user)
    MemberFactory(user=user)

    assert Member.objects.filter(user=user).count() == 2


# ---------- Project: unique (organisation, name) ----------


def test_project_name_unique_per_org():
    project = ProjectFactory(name="Bot")

    with pytest.raises(IntegrityError), transaction.atomic():
        Project.objects.create(organisation=project.organisation, name="Bot", slug="bot")


def test_same_project_name_allowed_in_two_orgs():
    ProjectFactory(name="Bot")
    ProjectFactory(name="Bot")

    assert Project.objects.filter(name="Bot").count() == 2


# ---------- EndUser: unique (project, external_id) ----------


def test_external_id_unique_per_project():
    end_user = EndUserFactory(external_id="u-1")

    with pytest.raises(IntegrityError), transaction.atomic():
        EndUser.objects.create(project=end_user.project, external_id="u-1")


def test_same_external_id_allowed_in_two_projects():
    # proves the constraint is scoped per project, not global
    EndUserFactory(external_id="u-1")
    EndUserFactory(external_id="u-1")

    assert EndUser.objects.filter(external_id="u-1").count() == 2


# ---------- ApiKey: unique prefix, unique key_hash, expiry check ----------


def test_api_key_prefix_is_unique():
    existing = ApiKeyFactory()

    with pytest.raises(IntegrityError), transaction.atomic():
        ApiKeyFactory(prefix=existing.prefix)


def test_api_key_hash_is_unique():
    existing = ApiKeyFactory()

    with pytest.raises(IntegrityError), transaction.atomic():
        ApiKeyFactory(key_hash=existing.key_hash)


def test_api_key_cannot_expire_before_creation():
    with pytest.raises(IntegrityError), transaction.atomic():
        ApiKeyFactory(expires_at=timezone.now() - timedelta(days=1))


def test_api_key_without_expiry_is_allowed():
    api_key = ApiKeyFactory(expires_at=None)

    assert ApiKey.objects.filter(pk=api_key.pk).exists()
