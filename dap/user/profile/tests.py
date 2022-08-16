from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker
from user.profile.models import Mentor, Mentee
from util.location.tests import LocationFactory
from user.core.academy.tests import AcademyFactory
from user.core.genre.const import GENRE_LIST
from user.core.genre.models import Genre
User = get_user_model()

class MentorFactory(DjangoModelFactory):
    class Meta:
        model = Mentor

    @classmethod
    def create(cls, **kwargs) -> Mentor:
        fake = Faker("ko_KR")
        genre_names = kwargs.get(
            "genre",
            fake.random_choices(elements=GENRE_LIST))
        genres = Genre.objects.filter(name__in=genre_names)
        academy_data = kwargs.get("academy", {})
        location_data = academy_data.get("location", {"type": "academy"})
        location = LocationFactory.create(**location_data)
        academy_data['location'] = location
        academy = AcademyFactory.create(**academy_data)

        mentor = Mentor.objects.create(
            description=kwargs.get("description", fake.sentence()),
            started_at=kwargs.get("started_at", fake.date_object())
        )
        mentor.academy.add(academy.id)
        mentor.genre.set(genres)
        return mentor


class MenteeFactory(DjangoModelFactory):
    class Meta:
        model = Mentee

    @classmethod
    def create(cls, **kwargs) -> Mentee:
        fake = Faker("ko_KR")
        genre_names = kwargs.get(
            "genre",
            fake.random_choices(elements=GENRE_LIST))
        genres = Genre.objects.filter(name__in=genre_names)
        mentee = Mentee.objects.create(
            description=kwargs.get("description", fake.sentence()),
            started_at=kwargs.get("started_at", fake.date_object())
        )
        mentee.genre.set(genres)
        return mentee
        