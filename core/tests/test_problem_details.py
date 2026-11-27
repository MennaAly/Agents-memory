"""Every error response uses Problem Details (RFC 9457)."""

import pytest

from core.modules.organisations.models import Member
from core.modules.organisations.serializers import ProjectSerializer
from core.tests.factories import MemberFactory, ProjectFactory

pytestmark = pytest.mark.django_db


def projects_url(org):
    return f"/api/v1/organisations/{org.id}/projects/"


def assert_problem(response, status, title):
    assert response.status_code == status
    assert response["Content-Type"] == "application/problem+json"
    body = response.json()
    assert body["type"] == "about:blank"
    assert body["title"] == title
    assert body["status"] == status
    assert body["detail"]
    assert body["instance"] == response.wsgi_request.path


def test_400_validation_error_lists_fields(owner_client, owner):
    response = owner_client.post(
        projects_url(owner.organisation), {"name": "x" * 201}, format="json"
    )

    assert_problem(response, 400, "Bad Request")
    assert response.json()["detail"] == "Invalid input."
    assert "name" in response.json()["errors"]


def test_400_wrong_type(owner_client, owner):
    response = owner_client.post(
        projects_url(owner.organisation), {"name": ["not", "a", "string"]}, format="json"
    )

    assert_problem(response, 400, "Bad Request")
    assert "name" in response.json()["errors"]


def test_401_keeps_www_authenticate_header(api_client):
    response = api_client.get("/api/v1/whoami/", HTTP_AUTHORIZATION="Bearer mem_bad_key")

    assert_problem(response, 401, "Unauthorized")
    assert response["WWW-Authenticate"] == "Bearer"


def test_403_member(api_client, owner):
    member = MemberFactory(organisation=owner.organisation, role=Member.Role.MEMBER)
    api_client.force_authenticate(user=member.user)

    response = api_client.post(projects_url(owner.organisation), {"name": "x"}, format="json")

    assert_problem(response, 403, "Forbidden")


def test_404_other_org(owner_client):
    project = ProjectFactory()

    response = owner_client.get(f"{projects_url(project.organisation)}{project.id}/")

    assert_problem(response, 404, "Not Found")


def test_409_conflict(owner_client, owner, monkeypatch):
    ProjectFactory(organisation=owner.organisation, name="Bot")
    monkeypatch.setattr(ProjectSerializer, "validate_name", lambda self, value: value)

    response = owner_client.post(projects_url(owner.organisation), {"name": "Bot"}, format="json")

    assert_problem(response, 409, "Conflict")
    assert response.json()["detail"] == "A project with this name already exists."
