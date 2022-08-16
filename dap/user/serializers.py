from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.models import update_last_login
from rest_framework.authtoken.models import Token
from dap.errors import AuthentificationFailed
from user.profile.serializers import MentorSerializer, MenteeSerializer
from dap.errors import FieldError
User = get_user_model()

class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
            'birth',
            'gender',
            'contact',
            'image',
            'mentor',
            'mentee'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'birth': {'input_formats': ['%Y-%m-%d']}
        }

    def create(self, validated_data: dict) -> dict[str, str]:
        user = User.objects.create(**validated_data)
        token, _ = Token.objects.get_or_create(user=user)
        return user, token.key
        
    
    def validate_gender(self, value: str) -> str:
        value = value.lower()
        if value not in ['male', 'female']:
            raise FieldError("wrong gender. [male, female]")
        return value


class UserLoginSerializer(serializers.Serializer):

    email = serializers.CharField(max_length=64, required=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data: dict) -> str:
        email = data.get('email', None)
        password = data.get('password', None)
        try:
            user = User.objects.get(email=email, password=password)
        except User.DoesNotExist:
            raise AuthentificationFailed("이메일 또는 비밀번호가 잘못되었습니다.")
        update_last_login(None, user)
        
        token, _ = Token.objects.get_or_create(user=user)
        return {
            'user': user,
            'token': token.key
        }


class UserRetrieveSerializer(serializers.ModelSerializer):
    mentor = serializers.SerializerMethodField()
    mentee = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'birth',
            'gender',
            'contact',
            'image',
            'mentor',
            'mentee'
        )
        extra_kwargs = {
            'birth': {'format': '%Y-%m-%d'}
        }

    def get_mentor(self, user):
        if user.mentor:
            return MentorSerializer(user.mentor).data
        return None

    def get_mentee(self, user):
        if user.mentee:
            return MenteeSerializer(user.mentee).data
        return None

class UserUpdateSerializer(serializers.ModelSerializer):
    mentor = serializers.SerializerMethodField()
    mentee = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'username',
            'first_name',
            'last_name',
            'password',
            'birth',
            'gender',
            'contact',
            'image',
            'mentor',
            'mentee'
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'birth': {'input_formats': ['%Y-%m-%d']}
        }

    def validate_gender(self, value: str) -> str:
        value = value.lower()
        if value not in ['male', 'female']:
            raise FieldError("wrong gender. [male, female]")
        return value

    def get_mentor(self, user):
        if user.mentor:
            return MentorSerializer(user.mentor).data
        return None

    def get_mentee(self, user):
        if user.mentee:
            return MenteeSerializer(user.mentee).data
        return None

class MentorSearchSerializer(serializers.ModelSerializer):
    academy = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'academy',
            'genre'
        )

    def get_genre(self, user):
        return list(user.mentor.genre.values_list('name', flat=True))

    def get_academy(self, user):
        return list(user.mentor.academy.values_list('name', flat=True))
