from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.core.academy.models import Academy
from dap.const import TIME_FORMAT
from dap.errors import FieldError, DuplicationError
from util.location.serializers import LocationSerializer

User = get_user_model()

    
class AcademySerializer(serializers.ModelSerializer):
    location = serializers.SerializerMethodField()

    class Meta:
        model = Academy
        fields = (
            'id',
            'name',
            'email',
            'contact',
            'description',
            'location',
            'started_at',
            'finished_at',
            'logo',
            'url',
            'location'
        )
        extra_kwargs = {
            'name': {'required': True},
            'started_at': TIME_FORMAT,
            'finished_at': TIME_FORMAT,
        }

    def create(self, validated_data: dict) -> Academy:
        location = self.context['location']
        location['type'] = "academy"
        ls = LocationSerializer(
            data=location, 
            context={
                'images': location.get('images'),
                'name': validated_data['name']
            }
        )
        ls.is_valid(raise_exception=True)
        location_ = ls.save()
        academy = Academy.objects.create(
            **validated_data,
            location=location_)
        return academy
    
    def validate(self, data: dict) -> dict:
        if not self.context.get('location'):
            raise FieldError("location required.")
        if data.get('started_at') and data.get('finished_at'):
            if data['started_at'] >= data['finished_at']:
                raise FieldError("finished_at should be later than started_at.")
        if Academy.objects.filter(
            name=data['name'],
            location__detail=self.context['location']['detail']
        ).exists():
            raise DuplicationError('academy already exists.')
        return data

    def get_location(self, academy):
        return LocationSerializer(academy.location).data


class AcademyListSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.detail')

    class Meta:
        model = Academy
        fields = (
            'id',
            'name',
            'location',
            'logo',
            'contact'
        )
