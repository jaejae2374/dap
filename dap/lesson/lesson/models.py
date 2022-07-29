from django.db import models
from user.core.academy.models import Academy
from user.core.genre.models import Genre
from django.contrib.auth import get_user_model
from util.location.models import Location
User = get_user_model()

class Lesson(models.Model):

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.CharField(max_length=1000, null=True, blank=True)
    started_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    academy = models.ForeignKey(Academy, on_delete=models.CASCADE, null=True)
    price = models.PositiveIntegerField(default=0)
    mentor = models.ManyToManyField(User, related_name="lessons")
    recruit_number = models.PositiveSmallIntegerField(default=0)
    genre = models.ManyToManyField(Genre, related_name="lessons")
    location = models.OneToOneField(Location, on_delete=models.CASCADE, null=True)

