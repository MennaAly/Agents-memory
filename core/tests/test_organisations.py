import pytest

from core.modules.organisations.models import Member, Organisation
from core.tests.factories import OrganisationFactory

URL = "/api/v1/organisations/"

# Every test in this file uses the database.
# (Same as putting @pytest.mark.django_db above each test.)
pytestmark = pytest.mark.django_db


def test_create_organisation_makes_creator_owner(auth_client, user):
    # Arrange: nothing to prepare, the fixtures did it
    # Act: call the endpoint like a real client would
    response = auth_client.post(URL, {"name": "Acme"}, format="json")

    # Assert: check the response first, then the database
    assert response.status_code == 201
    assert response.data["name"] == "Acme"

    org = Organisation.objects.get(pk=response.data["id"])
    member = Member.objects.get(organisation=org)
    assert member.user == user
    assert member.role == Member.Role.OWNER


def test_create_organisation_without_name_returns_400(auth_client):
    response = auth_client.post(URL, {}, format="json")

    assert response.status_code == 400
    assert "name" in response.data  # the error is attached to the `name` field
    assert Organisation.objects.count() == 0  # nothing was saved


def test_list_only_shows_my_organisations(auth_client, user):
    # Arrange: one org I belong to, one I don't
    mine = OrganisationFactory(name="Mine")
    Member.objects.create(user=user, organisation=mine, role=Member.Role.OWNER)
    OrganisationFactory(name="Not mine")

    response = auth_client.get(URL)

    assert response.status_code == 200
    names = [org["name"] for org in response.data]
    assert names == ["Mine"]


def test_logged_out_user_is_rejected(api_client):
    response = api_client.post(URL, {"name": "Acme"}, format="json")

    assert response.status_code == 403
