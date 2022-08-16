from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.core.academy.serializers import AcademySerializer
from user.profile.models import Mentor, Mentee
from dap.errors import FieldError
from dap.const import DATE_FORMAT
from dap.utils import merge_dicts

User = get_user_model()

class MentorSerializer(serializers.ModelSerializer):
    genre = serializers.SerializerMethodField()
    academy = serializers.SerializerMethodField()

    class Meta:
        model = Mentor
        fields = (
            'started_at',
            'description',
            'academy',
            'genre'
        )
        extra_kwargs = {
            'started_at': merge_dicts(
                {'required': True},
                DATE_FORMAT
            ),
        }

    def create(self, validated_data: dict) -> Mentor:
        mentor = Mentor.objects.create(**validated_data)
        mentor.genre.set(self.context['genres'])
        mentor.academy.set(self.context['academies'])
        return mentor
    
    def validate(self, data: dict) -> dict:
        if not self.context.get('genres'):
            raise FieldError("genres required.")
        if not self.context.get('academies'):
            raise FieldError("academies required.")
        return data

    def get_genre(self, mentor):
        return mentor.genre.values_list('name', flat=True)

    def get_academy(self, mentor):
        return AcademySerializer(mentor.academy.all(), many=True).data
    
        
class MenteeSerializer(serializers.ModelSerializer):
    genre = serializers.SerializerMethodField()

    class Meta:
        model = Mentee
        fields = (
            'started_at',
            'description',
            'courses_count',
            'genre',
            'tier'
        )
        extra_kwargs = {
            'started_at': merge_dicts(
                {'required': True},
                DATE_FORMAT
            )
        }

    def create(self, validated_data: dict) -> Mentee:
        mentee = Mentee.objects.create(
            started_at = validated_data['started_at'],
            description = validated_data.get('description')
        )
        mentee.genre.set(self.context['genres'])
        return mentee
    
    def validate(self, data: dict) -> dict:
        if not self.context.get('genres'):
            raise FieldError("genres required.")
        return data

    def get_genre(self, mentee):
        return mentee.genre.values_list('name', flat=True)


class MentorUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentor
        fields = (
            "started_at",
            "description"
        )
        extra_kwargs = {
            'started_at': merge_dicts(
                {'required': True},
                DATE_FORMAT
            )
        }

class MenteeUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mentee
        fields = (
            "started_at",
            "description"
        )
        extra_kwargs = {
            'started_at': merge_dicts(
                {'required': True},
                DATE_FORMAT
            )
        }
