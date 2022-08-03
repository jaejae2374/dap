from rest_framework import serializers
from user.serializers import UserRetrieveSerializer
from user.core.academy.serializers import AcademySerializer
from lesson.lesson.models import Lesson
from util.location.serializers import LocationSerializer
from dap.errors import FieldError

class LessonCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lesson
        fields = (
            'title',
            'description',
            'started_at',
            'finished_at',
            'academy',
            'price',
            'recruit_number'
        )
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
        lesson.save()
        lesson.genre.set(self.context['genres'])
        lesson.mentor.set(self.context['mentors'])
        return lesson

    def validate(self, data: dict) -> dict:
        if not self.context.get('location'):
            raise FieldError("location required.")
        if not self.context.get('mentors'):
            raise FieldError("mentors required.")
        if not self.context.get('genres'):
            raise FieldError("genres required.")
        if data.get('started_at') and data.get('finished_at'):
            if data['started_at'] >= data['finished_at']:
                raise FieldError("finished_at should be later than started_at.")
        if data.get('price', 0) < 0:
            raise FieldError("price should be positive.")
        if data.get('recruit_number', 0) < 0:
            raise FieldError("recruit_number should be positive.")

        return data

class LessonListSerializer(serializers.ModelSerializer):
    mentors = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()
    academy = serializers.CharField(source="academy.name")
    location = serializers.CharField(source="location.detail")

    class Meta:
        model = Lesson
        fields = (
            'id',
            'title',
            'started_at',
            'finished_at',
            'price',
            'recruit_number',
            'mentors',
            'academy',
            'genres',
            'location'
        )
        extra_kwargs = {
            'started_at': {'format': '%Y-%m-%dT%H:%M'},
            'finished_at': {'format': '%Y-%m-%dT%H:%M'}
        }

    def get_genres(self, lesson):
        return lesson.genre.all().values_list('name', flat=True)

    def get_mentors(self, lesson):
        return lesson.mentor.all().values_list('id', 'username')

class LessonRetrieveSerializer(serializers.ModelSerializer):
    mentors = serializers.SerializerMethodField()
    academy = serializers.SerializerMethodField()
    genres = serializers.SerializerMethodField()
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
            'mentors',
            'academy',
            'genres',
            'location'
        )
        extra_kwargs = {
            'started_at': {'format': '%Y-%m-%dT%H:%M'},
            'finished_at': {'format': '%Y-%m-%dT%H:%M'}
        }

    def get_academy(self, lesson):
        academy = lesson.academy
        #TODO: add academy logo
        return {
            'id': academy.id,
            'name': academy.name,
            'contact': academy.contact
        }

    def get_genres(self, lesson):
        return lesson.genre.all().values_list('name', flat=True)

    def get_location(self, lesson):
        return LocationSerializer(lesson.location).data

    def get_mentors(self, lesson):
        return UserRetrieveSerializer(lesson.mentor.all(), many=True).data
