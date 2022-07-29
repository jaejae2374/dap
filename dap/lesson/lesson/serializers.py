from rest_framework import serializers
from user.serializers import UserRetrieveSerializer
from user.core.academy.serializers import AcademySerializer
from lesson.lesson.models import Lesson
from util.location.serializers import LocationSerializer
from dap.errors import FieldError

class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = '__all__'
        extra_kwargs = {
            'started_at': {'input_formats': ['%Y-%m-%dT%H:%M']},
            'finished_at': {'input_formats': ['%Y-%m-%dT%H:%M']},
            'title': {'required': True},
        }

    
    def create(self, validated_data: dict) -> Lesson:
        lesson = Lesson.objects.create(**validated_data)
        location = self.context['location']
        location['type'] = "lesson"
        ls = LocationSerializer(
            data=location, 
            context={
                'images': location.get('images'),
                'name': str(lesson.id)
            }
        )
        ls.is_valid(raise_exception=True)
        location_ = ls.save()
        lesson.location = location_
        lesson.genre.set(self.context['genres'])
        lesson.genre.set(self.context['mentors'])
        # lesson.save()
        return lesson

    def validate(self, data: dict) -> dict:
        if not self.context.get('location'):
            raise FieldError("location required.")
        if not self.context.get('mentors'):
            raise FieldError("mentor required.")
        if not self.context.get('genres'):
            raise FieldError("mentor required.")
        if data.get('started_at') and data.get('finished_at'):
            if data['started_at'] >= data['finished_at']:
                raise FieldError("finished_at should be later than started_at.")
        if data.get('price', 0) < 0:
            raise FieldError("price should be positive.")
        if data.get('recruit_number', 0) < 0:
            raise FieldError("recruit_number should be positive.")

        return data

class LessonRetrieveSerializer(serializers.ModelSerializer):
    mentor = serializers.SerializerMethodField()
    academy = serializers.SerializerMethodField()
    genre = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = (
            'title',
            'description',
            'started_at',
            'finished_at',
            'price',
            'recruit_number',
            'mentor',
            'academy',
            'genre',
            'location'
        )
        extra_kwargs = {
            'started_at': {'format': '%Y-%m-%dT%H:%M'},
            'finished_at': {'format': '%Y-%m-%dT%H:%M'}
        }

    def get_academy(self, lesson):
        return AcademySerializer(lesson.academy).data

    def get_genre(self, lesson):
        return lesson.genre.all().values_list('name', flat=True)

    def get_location(self, lesson):
        return LocationSerializer(lesson.location).data

    def get_mentor(self, lesson):
        return UserRetrieveSerializer(lesson.mentor.all(), many=True).data
