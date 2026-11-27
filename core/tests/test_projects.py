"""
Project endpoints: create, list, retrieve, update, delete.
Covers 201, 400 (missing / too long / duplicate name), 403 (role), 404 (other org).
"""

import pytest

from core.modules.organisations.models import Member, Project
from core.tests.factories import MemberFactory, ProjectFactory

pytestmark = pytest.mark.django_db


def projects_url(org):
    return f"/api/v1/organisations/{org.id}/projects/"


def project_url(project):
    return f"{projects_url(project.organisation)}{project.id}/"


@pytest.fixture
def member_client(api_client, owner):
    # a plain MEMBER of the owner's org (same org, lower role)
    member = MemberFactory(organisation=owner.organisation, role=Member.Role.MEMBER)
    api_client.force_authenticate(user=member.user)
    return api_client


# ---------- create ----------


def test_create_project(owner_client, owner):
    org = owner.organisation
    response = owner_client.post(projects_url(org), {"name": "project1"}, format="json")

    assert response.status_code == 201
    assert response.data["name"] == "project1"
    # the server set the read-only fields
    project = Project.objects.get(pk=response.data["id"])
    assert project.organisation == org
    assert project.slug == "project1"


def test_create_ignores_organisation_and_slug_from_body(owner_client, owner):
    other = ProjectFactory()  # a project in an org the owner is NOT in
    response = owner_client.post(
        projects_url(owner.organisation),
        {"name": "My App", "organisation": other.organisation.id, "slug": "hacked"},
        format="json",
    )

    assert response.status_code == 201
    project = Project.objects.get(pk=response.data["id"])
    assert project.organisation == owner.organisation
    assert project.slug == "my-app"


def test_duplicate_project(owner_client, owner):
    org = owner.organisation
    ProjectFactory(organisation=org, name="project1")  # arrange with the factory, not a POST

    response = owner_client.post(projects_url(org), {"name": "project1"}, format="json")

    assert response.status_code == 400
    assert "name" in response.data
    assert Project.objects.filter(organisation=org).count() == 1


def test_same_name_allowed_in_another_org(owner_client, owner):
    ProjectFactory(name="project1")  # same name, different org

    response = owner_client.post(
        projects_url(owner.organisation), {"name": "project1"}, format="json"
    )

    assert response.status_code == 201


def test_missing_name_in_project_req(owner_client, owner):
    response = owner_client.post(projects_url(owner.organisation), {}, format="json")

    assert response.status_code == 400
    assert "name" in response.data
    assert Project.objects.count() == 0


def test_name_too_long(owner_client, owner):
    response = owner_client.post(
        projects_url(owner.organisation), {"name": "x" * 201}, format="json"
    )

    assert response.status_code == 400
    assert "name" in response.data


def test_create_project_with_member_role(member_client, owner):
    # valid body, logged in, same org: the ONLY reason to fail is the role
    response = member_client.post(
        projects_url(owner.organisation), {"name": "project1"}, format="json"
    )

    assert response.status_code == 403
    assert Project.objects.count() == 0


def test_create_project_logged_out(api_client, owner):
    response = api_client.post(
        projects_url(owner.organisation), {"name": "project1"}, format="json"
    )

    assert response.status_code == 403


# ---------- list ----------


def test_list_only_shows_this_orgs_projects(owner_client, owner):
    ProjectFactory(organisation=owner.organisation, name="mine")
    ProjectFactory(name="not mine")  # other org

    response = owner_client.get(projects_url(owner.organisation))

    assert response.status_code == 200
    names = [p["name"] for p in response.data["results"]]  # paginated response
    assert names == ["mine"]


def test_list_is_paginated_newest_first(owner_client, owner):
    for i in range(3):
        ProjectFactory(organisation=owner.organisation, name=f"p{i}")

    response = owner_client.get(projects_url(owner.organisation))

    assert set(response.data) == {"next", "previous", "results"}
    assert [p["name"] for p in response.data["results"]] == ["p2", "p1", "p0"]


# ---------- retrieve / update / delete ----------


def test_project_in_other_org_returns_404(owner_client):
    project = ProjectFactory()  # org the owner is NOT in

    response = owner_client.get(project_url(project))

    assert response.status_code == 404


def test_member_can_retrieve(member_client, owner):
    project = ProjectFactory(organisation=owner.organisation)

    response = member_client.get(project_url(project))

    assert response.status_code == 200


def test_owner_rename_updates_slug(owner_client, owner):
    project = ProjectFactory(organisation=owner.organisation, name="Old Name")

    response = owner_client.patch(project_url(project), {"name": "New Name"}, format="json")

    assert response.status_code == 200
    project.refresh_from_db()  # reload from the DB, the object in memory is stale
    assert project.name == "New Name"
    assert project.slug == "new-name"


def test_owner_can_save_same_name(owner_client, owner):
    # validate_name must ignore the project itself
    project = ProjectFactory(organisation=owner.organisation, name="Same")

    response = owner_client.patch(project_url(project), {"name": "Same"}, format="json")

    assert response.status_code == 200


def test_member_cannot_update(member_client, owner):
    project = ProjectFactory(organisation=owner.organisation, name="Before")

    response = member_client.patch(project_url(project), {"name": "After"}, format="json")

    assert response.status_code == 403
    project.refresh_from_db()
    assert project.name == "Before"


def test_owner_can_delete(owner_client, owner):
    project = ProjectFactory(organisation=owner.organisation)

    response = owner_client.delete(project_url(project))

    assert response.status_code == 204
    assert not Project.objects.filter(pk=project.pk).exists()


def test_member_cannot_delete(member_client, owner):
    project = ProjectFactory(organisation=owner.organisation)

    response = member_client.delete(project_url(project))

    assert response.status_code == 403
    assert Project.objects.filter(pk=project.pk).exists()
