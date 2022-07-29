from django.db import models

class Location(models.Model):
    """Location Model.

    Attributes:
        type (str): location's type. ex) Academy, Lesson...
        detail (str): detail location.
        city (str): location's city.
        district (str): location's district.
        description (str): location's detail description.
    """
    LOCATION_TYPE = (
        ("academy", "academy"),
        ("lesson", "lesson")
    )

    id = models.AutoField(primary_key=True)
    type = models.CharField(max_length=20, choices=LOCATION_TYPE)
    detail = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    

class LocationImage(models.Model):
    """Location Image Model.

    Attributes:
        name (str): location's name.
        image (Image): location's image.
    """
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name="images")
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=f"academy/{name}/location", null=True)
