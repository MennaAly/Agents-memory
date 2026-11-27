"""Factories build valid model objects for tests with one line, e.g. UserFactory().

Every field gets a sensible default; a test overrides only what it cares about:
    UserFactory(username="alice")
"""

import factory
from django.contrib.auth import get_user_model
from django.utils.text import slugify

from core.modules.api_key.models import ApiKey
from core.modules.api_key.services import generate_key, hash_key
from core.modules.organisations.models import EndUser, Member, Organisation, Project


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



class EndUserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = EndUser

    project = factory.SubFactory(ProjectFactory)
    external_id = factory.Sequence(lambda n: f"end-user-{n}")


class ApiKeyFactory(factory.django.DjangoModelFactory):
    """ApiKeyFactory() returns a saved key; the raw secret is on key.full_key.

    Only the hash is stored in the DB, so the factory keeps the raw key on the
    object for tests that need to send it in an Authorization header.
    """

    class Meta:
        model = ApiKey

    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f"key-{n}")
    full_key = factory.LazyFunction(lambda: generate_key()[0])
    prefix = factory.LazyAttribute(lambda obj: obj.full_key[:12])  # "mem_" + 8 hex chars
    key_hash = factory.LazyAttribute(lambda obj: hash_key(obj.full_key))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        full_key = kwargs.pop("full_key")  # not a model field: remove before saving
        api_key = super()._create(model_class, *args, **kwargs)
        api_key.full_key = full_key
        return api_key
