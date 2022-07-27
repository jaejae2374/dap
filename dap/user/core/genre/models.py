from django.db import models
from user.core.genre.const import GENRE_CHOCIES, DEFAULT

class Genre(models.Model):
    """Static Genre Model.

    Attributes:
        name (str): genre's name.
        description (str): genre's description.
        video (File): genre's representative video.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, choices=GENRE_CHOCIES)
    description = models.CharField(max_length=1000, blank=True, null=True)
    video = models.FileField(upload_to=f"genre/{name}/video", null=True)

    def __str__(self) -> str:
        return self.name
