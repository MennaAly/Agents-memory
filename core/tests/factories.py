"""Factories build valid model objects for tests with one line, e.g. UserFactory().

Every field gets a sensible default; a test overrides only what it cares about:
    UserFactory(username="alice")
"""

import factory
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from core.modules.organisations.models import Member, Organisation, Project


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    password = factory.django.Password("password")


class OrganisationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Organisation

    name = factory.Faker("company")


class MemberFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Member

    user = factory.SubFactory(UserFactory)
    organisation = factory.SubFactory(OrganisationFactory)
    role = Member.Role.MEMBER  # override in tests: MemberFactory(role=Member.Role.OWNER)


class ProjectFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Project

    organisation = factory.SubFactory(OrganisationFactory)
    name = factory.Sequence(lambda n: f"project-{n}")
    slug = factory.LazyAttribute(lambda obj: slugify(obj.name))

