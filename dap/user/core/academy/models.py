from django.db import models

class AcademyLocation(models.Model):
    """Academy Location Model.

    Attributes:
        detail (str): detail location.
        city (str): location's city.
        district (str): location's district.
        description (str): location's detail description.
    """

    id = models.AutoField(primary_key=True)
    detail = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=20, blank=True, null=True)
    district = models.CharField(max_length=20, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    

class AcademyLocationImage(models.Model):
    """Academy Location Image Model.

    Attributes:
        name (str): location's name.
        image (Image): location's image.
    """
    location = models.ForeignKey(AcademyLocation, on_delete=models.CASCADE, related_name="images")
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to=f"academy/{name}/location", null=True)

class Academy(models.Model):
    """Academy Model.

    Attributes:
        name (str): academy's name.
        email (str): academy's email.
        contact (str): academy's contact number.
        description (str): academy's specific description.
        started_at (DateTime): academy's open time.
        finished_at (DateTime): academy's end time.
        logo (Image): academy's representative image, logo.
        url (str): academy's website url.
        location (AcademyLocation): academy's location model.
    """
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=30)
    email = models.EmailField(max_length=64, unique=True, blank=True, null=True)
    contact = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    started_at = models.DateTimeField(blank=True, null=True)
    finished_at = models.DateTimeField(blank=True, null=True)
    logo = models.ImageField(upload_to=f"academy/{name}/logo", null=True)
    url = models.CharField(blank=True, null=True, max_length=500)
    location = models.OneToOneField(AcademyLocation, on_delete=models.CASCADE, null=True)
    

