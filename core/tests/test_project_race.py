"""Duplicate project names under a race: the DB constraint is the last line of defence.

Two kinds of test:

1. Simulated race (normal `django_db`, fast): we switch off validate_name so the
   request reaches the DB, exactly like the losing request in a real race.

2. Real race (`django_db(transaction=True)`): two threads POST at the same time.
   Normal tests wrap everything in one transaction that is rolled back at the end,
   so other DB connections (like a second thread) can't see the test's data.
   transaction=True (= Django's TransactionTestCase) really commits and then
   empties the tables after the test: slower, but needed for multiple connections.
"""

import threading

import pytest
from django.db import connection
from rest_framework.test import APIClient

from core.modules.organisations.models import Project
from core.modules.organisations.serializers import ProjectSerializer
from core.tests.factories import ProjectFactory


def projects_url(org):
    return f"/api/v1/organisations/{org.id}/projects/"


@pytest.mark.django_db
def test_db_duplicate_returns_409_not_500(owner_client, owner, monkeypatch):
    ProjectFactory(organisation=owner.organisation, name="Bot")
    # pretend the other request saved "Bot" after our validation ran
    monkeypatch.setattr(ProjectSerializer, "validate_name", lambda self, value: value)

    response = owner_client.post(projects_url(owner.organisation), {"name": "Bot"}, format="json")

    assert response.status_code == 409
    assert Project.objects.filter(name="Bot").count() == 1


@pytest.mark.django_db
def test_db_duplicate_on_rename_returns_409(owner_client, owner, monkeypatch):
    ProjectFactory(organisation=owner.organisation, name="Taken")
    project = ProjectFactory(organisation=owner.organisation, name="Free")
    monkeypatch.setattr(ProjectSerializer, "validate_name", lambda self, value: value)

    response = owner_client.patch(
        f"{projects_url(owner.organisation)}{project.id}/", {"name": "Taken"}, format="json"
    )

    assert response.status_code == 409
    project.refresh_from_db()
    assert project.name == "Free"


@pytest.mark.django_db(transaction=True)
def test_concurrent_creates_never_500_and_never_duplicate(owner):
    url = projects_url(owner.organisation)
    start = threading.Barrier(2)  # both threads wait here, then go at the same moment
    statuses = []

    def create():
        client = APIClient()
        client.force_authenticate(user=owner.user)
        start.wait()
        statuses.append(client.post(url, {"name": "Race"}, format="json").status_code)
        connection.close()  # each thread opened its own DB connection

    threads = [threading.Thread(target=create) for _ in range(2)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    # one wins; the other is stopped by validate_name (400) or by the DB (409)
    assert sorted(statuses)[0] == 201
    assert sorted(statuses)[1] in (400, 409)
    assert Project.objects.filter(name="Race").count() == 1
