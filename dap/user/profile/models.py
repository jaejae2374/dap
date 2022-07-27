from django.db import models
from user.core.genre.models import Genre
from user.core.academy.models import Academy
from user.profile.const import TIER, UN

class Profile(models.Model):
    """Base Profile Model."""

    started_at = models.DateField()
    description = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        abstract = True


class Mentor(Profile):
    """Mentor Profile Model.

    Attributes:
        started_at (Date): career of mentor.
        genre (Genre): genre of mentor.
        academy (Academy): academy of mentor.
        description (str): descriptions of mentor.
    """
    id = models.AutoField(primary_key=True)
    genre = models.ManyToManyField(Genre, related_name="mentors")
    academy = models.ManyToManyField(Academy, related_name="mentors")

class Mentee(Profile):
    """Mentee Profile Model.

    Attributes:
        started_at (Date): career of mentee.
        genre (Genre): genre of mentee.
        description (str): descriptions of mentee.
        courses_count (int): counts of courses mentee get.
        tier (str): tier of mentee according to courses_count. 
    """

    id = models.AutoField(primary_key=True)
    courses_count = models.SmallIntegerField(default=0)
    tier = models.CharField(max_length=10, choices=TIER, default=UN)
    genre = models.ManyToManyField(Genre, related_name="mentees")
    
