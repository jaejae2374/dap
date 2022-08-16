from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker
from util.location.models import Location
User = get_user_model()

class LocationFactory(DjangoModelFactory):
    class Meta:
        model = Location

    @classmethod
    def create(cls, **kwargs) -> Location:
        fake = Faker("ko_KR")
        fake_city = fake.random_choices(
            elements=(
                ['서울시', '강남구'],
                ['서울시', '서초구'],
                ['서울시', '관악구'],
                ['용인시', '수지구'],
                ['용인시', '분당구'],
                ['용인시', '영통구']),
            length=1
        )[0]
        return Location.objects.create(
            type=kwargs["type"],
            detail=kwargs.get("detail", fake.address()),
            city=kwargs.get("city", fake_city[0]),
            district=kwargs.get("district", fake_city[1]),
            description=kwargs.get("description", fake.sentence())
        )

        