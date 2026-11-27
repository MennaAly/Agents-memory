"""API keys: services, Bearer authentication, scopes, and the create/revoke endpoints."""

from datetime import timedelta

import pytest
from django.utils import timezone

from core.modules.api_key.models import ApiKey
from core.modules.api_key.services import (
    create_api_key,
    find_valid_key,
    generate_key,
    hash_key,
    revoke_api_key,
)
from core.modules.organisations.models import Member
from core.tests.factories import ApiKeyFactory, MemberFactory, ProjectFactory

pytestmark = pytest.mark.django_db

WHOAMI_URL = "/api/v1/whoami/"


def keys_url(project):
    return f"/api/v1/projects/{project.id}/keys/"


def revoke_url(api_key):
    return f"/api/v1/projects/{api_key.project_id}/keys/{api_key.id}/revoke/"


@pytest.fixture
def project(owner):
    return ProjectFactory(organisation=owner.organisation)


# ---------- services ----------


def test_generate_key_format():
    full_key, prefix = generate_key()

    assert prefix.startswith("mem_") and len(prefix) == 12
    assert full_key.startswith(prefix + "_")


def test_create_api_key_stores_only_the_hash(project, owner):
    api_key, full_key = create_api_key(project, owner.user, "ci", True, False, False)

    assert api_key.key_hash == hash_key(full_key)
    assert full_key not in api_key.key_hash  # the raw secret is never stored


def test_find_valid_key_returns_key_and_sets_last_used():
    api_key = ApiKeyFactory()

    found = find_valid_key(api_key.full_key)

    assert found == api_key
    assert found.last_used_at is not None


def test_find_valid_key_rejects_revoked_key():
    api_key = ApiKeyFactory(revoked_at=timezone.now())

    assert find_valid_key(api_key.full_key) is None


def test_find_valid_key_rejects_expired_key():
    api_key = ApiKeyFactory(expires_at=timezone.now() + timedelta(hours=1))
    # A past expiry can't be inserted (CheckConstraint: expiry > creation),
    # so move both timestamps into the past with a direct UPDATE.
    ApiKey.objects.filter(pk=api_key.pk).update(
        created_at=timezone.now() - timedelta(hours=2),
        expires_at=timezone.now() - timedelta(hours=1),
    )

    assert find_valid_key(api_key.full_key) is None


def test_find_valid_key_rejects_unknown_key():
    assert find_valid_key("mem_00000000_not-a-real-key") is None


def test_revoke_is_idempotent():
    api_key = ApiKeyFactory()

    revoke_api_key(api_key)
    first = api_key.revoked_at
    revoke_api_key(api_key)

    assert first is not None
    assert api_key.revoked_at == first  # second call doesn't move the timestamp


# ---------- authentication + scopes (whoami) ----------


def test_whoami_with_valid_key(api_client):
    api_key = ApiKeyFactory(can_read=True)

    response = api_client.get(WHOAMI_URL, HTTP_AUTHORIZATION=f"Bearer {api_key.full_key}")

    assert response.status_code == 200
    assert response.data == {
        "project_id": api_key.project_id,
        "key_name": api_key.name,
        "prefix": api_key.prefix,
    }


@pytest.mark.parametrize(
    "header",
    [None, "Bearer mem_00000000_wrong", "Bearer a b"],
    ids=["no-header", "wrong-key", "malformed"],
)
def test_whoami_rejects_bad_credentials(api_client, header):
    kwargs = {"HTTP_AUTHORIZATION": header} if header else {}

    response = api_client.get(WHOAMI_URL, **kwargs)

    assert response.status_code == 401
    assert response["WWW-Authenticate"] == "Bearer"


def test_whoami_rejects_revoked_key(api_client):
    api_key = ApiKeyFactory()
    revoke_api_key(api_key)

    response = api_client.get(WHOAMI_URL, HTTP_AUTHORIZATION=f"Bearer {api_key.full_key}")

    assert response.status_code == 401


def test_whoami_without_read_scope_returns_403(api_client):
    api_key = ApiKeyFactory(can_read=False)

    response = api_client.get(WHOAMI_URL, HTTP_AUTHORIZATION=f"Bearer {api_key.full_key}")

    assert response.status_code == 403


# ---------- create endpoint ----------


def test_owner_creates_key_and_sees_secret_once(owner_client, project):
    response = owner_client.post(keys_url(project), {"name": "ci"}, format="json")

    assert response.status_code == 201
    full_key = response.data["key"]
    api_key = ApiKey.objects.get(pk=response.data["id"])
    assert api_key.project == project
    assert api_key.key_hash == hash_key(full_key)
    assert "key_hash" not in response.data  # the hash is never returned


def test_create_key_scopes_and_expiry(owner_client, project):
    expires = timezone.now() + timedelta(days=30)
    response = owner_client.post(
        keys_url(project),
        {"name": "writer", "can_write": True, "expires_at": expires.isoformat()},
        format="json",
    )

    assert response.status_code == 201
    api_key = ApiKey.objects.get(pk=response.data["id"])
    assert api_key.can_read and api_key.can_write and not api_key.can_delete
    assert api_key.expires_at is not None


def test_create_key_with_past_expiry_returns_400(owner_client, project):
    past = (timezone.now() - timedelta(days=1)).isoformat()

    response = owner_client.post(
        keys_url(project), {"name": "old", "expires_at": past}, format="json"
    )

    assert response.status_code == 400
    assert ApiKey.objects.count() == 0


def test_create_key_missing_name_returns_400(owner_client, project):
    response = owner_client.post(keys_url(project), {}, format="json")

    assert response.status_code == 400


def test_member_cannot_create_key(api_client, project):
    member = MemberFactory(organisation=project.organisation, role=Member.Role.MEMBER)
    api_client.force_authenticate(user=member.user)

    response = api_client.post(keys_url(project), {"name": "ci"}, format="json")

    assert response.status_code == 403
    assert ApiKey.objects.count() == 0


def test_create_key_in_other_org_returns_404(owner_client):
    other_project = ProjectFactory()

    response = owner_client.post(keys_url(other_project), {"name": "ci"}, format="json")

    assert response.status_code == 404


# ---------- revoke endpoint ----------


def test_owner_revokes_key(owner_client, project):
    api_key = ApiKeyFactory(project=project)

    response = owner_client.post(revoke_url(api_key))

    assert response.status_code == 200
    api_key.refresh_from_db()
    assert api_key.revoked_at is not None


def test_member_cannot_revoke_key(api_client, project):
    api_key = ApiKeyFactory(project=project)
    member = MemberFactory(organisation=project.organisation, role=Member.Role.MEMBER)
    api_client.force_authenticate(user=member.user)

    response = api_client.post(revoke_url(api_key))

    assert response.status_code == 403
    api_key.refresh_from_db()
    assert api_key.revoked_at is None


def test_revoke_key_in_other_org_returns_404(owner_client):
    api_key = ApiKeyFactory()  # its project is in another org

    response = owner_client.post(revoke_url(api_key))

    assert response.status_code == 404
