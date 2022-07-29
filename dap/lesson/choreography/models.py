from django.db import models
from django.contrib.auth import get_user_model
from lesson.lesson.models import Lesson
User = get_user_model()


class Choreography(models.Model):
    id = models.AutoField()
    lesson = models.OneToOneField(Lesson, on_delete=models.SET_NULL, null=True)
    title = models.CharField(max_length=50)
    song = models.CharField(max_length=50)
    mentor = models.ManyToManyField(User, related_name="choreography")
    reference = models.FileField(upload_to=f"", null=True)
    work = models.FileField(upload_to=f"lesson/{lesson}/choreography", null=True)
