from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractUser
from user.profile.models import Mentor, Mentee


class CustomUserManager(BaseUserManager):
    """Custom User Manager."""
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create user."""
        if not email:
            raise ValueError('이메일을 설정해주세요.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create active user."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create super user."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True or extra_fields.get('is_superuser') is not True:
            raise ValueError('권한 설정이 잘못되었습니다.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Base User Model.

    Attributes:
        email (str): user's email.
        username (str): user's nickname.
        first_name (str): user's first_name.
        last_name (str): user's last_name.
        password (str): user's password.
        birth (Date): user's birth.
        gender (str): user's gender. male or female.
        contact (str): user's phone number.
        last_login (DateTime): user's last login.
        created_at (DateTime): date when user joined.
        is_staff (bool): whether user is staff.
        is_superuser (bool): whether user is superuser.
        mentor (Mentor): Mentor profile if user is mentor.
        mentee (Mentee): Mentee profile if user is mentee.
        image (Image): profile image of user.
    """

    objects = CustomUserManager()

    id = models.AutoField(primary_key=True)
    email = models.EmailField(max_length=64, unique=True)
    username = models.CharField(max_length=12)
    # TODO: Valiedate username's integrity if mentee.
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    password = models.CharField(max_length=32)
    birth = models.DateField()
    gender = models.CharField(max_length=10)
    contact = models.CharField(max_length=20, unique=True, null=True)
    last_login = models.DateTimeField(auto_now=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    mentor = models.OneToOneField(Mentor, on_delete=models.CASCADE, null=True)
    mentee = models.OneToOneField(Mentee, on_delete=models.CASCADE, null=True)
    image = models.ImageField(null=True, upload_to=f"{email}/profile_image")

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'birth', 'gender']
    
    def __str__(self):
        return self.username

    def get_full_name(self):
        return self.first_name + self.last_name
