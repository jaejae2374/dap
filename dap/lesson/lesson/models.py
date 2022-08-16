from django.db import models
from user.core.academy.models import Academy
from user.core.genre.models import Genre
from django.contrib.auth import get_user_model
from util.location.models import Location
User = get_user_model()

class Lesson(models.Model):
    """Lesson Model.

    Attributes:
        title (str): lesson's name.
        description (str): lesson's specific description.
        started_at (DateTime): lesson's start time.
        finished_at (DateTime): lesson's finish time.
        academy (Academy): academy where lesson takes.
        price (PositiveInt): lesson's price.
        mentor (User): lesson's mentors.
        recruit_number (PositiveSmallInt): lesson's recruit number.
        genre (Genre): lesson's genre.
        location (Location): lesson's location.
    """
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    academy = models.ForeignKey(Academy, on_delete=models.CASCADE, null=True)
    price = models.PositiveIntegerField(default=0)
    mentor = models.ManyToManyField(User, related_name="lessons")
    recruit_number = models.PositiveSmallIntegerField(default=0)
    genre = models.ForeignKey(Genre, on_delete=models.PROTECT, null=True)
    location = models.OneToOneField(Location, on_delete=models.CASCADE, null=True)
    mentee = models.ManyToManyField(User, related_name="classes")

    class Meta:
        ordering = ['-started_at']
