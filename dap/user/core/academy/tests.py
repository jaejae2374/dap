from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker
from user.core.academy.models import Academy
User = get_user_model()

class AcademyFactory(DjangoModelFactory):
    class Meta:
        model = Academy

    @classmethod
    def create(cls, **kwargs) -> Academy:
        fake = Faker("ko_KR")
        return Academy.objects.create(
            name=kwargs.get("name", fake.name()),
            email=kwargs.get("email", fake.email()),
            contact=kwargs.get("contact", fake.phone_number()),
            description=kwargs.get("description", fake.sentence()),
            location=kwargs.get("location")
        )
