import pytest
from rest_framework.test import APIClient

from core.modules.organisations.models import Member
from core.tests.factories import MemberFactory, UserFactory


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def auth_client(api_client, user):
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def owner(db):
    return MemberFactory(role=Member.Role.OWNER)

@pytest.fixture
def owner_client(api_client, owner):
    api_client.force_authenticate(user=owner.user)
    return api_client
