from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.core.academy.models import Academy, AcademyLocation, AcademyLocationImage
from dap.const import TIME_FORMAT
from dap.errors import FieldError, DuplicationError

User = get_user_model()

class AcademyLocationImageSerializer(serializers.ModelSerializer):
    class Meta: 
        model = AcademyLocationImage
        fields = (
            'id',
            'image'
        )

class AcademyLocationSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = AcademyLocation
        fields = (
            'id',
            'detail',
            'city',
            'district',
            'description',
            'images'
        )
        extra_kwargs = {
            'detail': {'required': True}
        }

    def create(self, validated_data: dict) -> AcademyLocation:
        # TODO: parsing detail to city, district method.
        academy_location = AcademyLocation.objects.create(
            detail = validated_data['detail'],
            city = validated_data.get('city'),
            district = validated_data.get('district'),
            description = validated_data.get('description')
        )
        if self.context.get('images'):
            AcademyLocationImage.objects.bulk_create(
                [
                    AcademyLocationImage(
                        location=academy_location,
                        name=self.context['name'],
                        image=image
                    ) for image in self.context['images']
                ]
            )
        return academy_location

    def get_images(self, academy_location: AcademyLocation):
        if academy_location.images:
            return AcademyLocationImageSerializer(academy_location.images, many=True).data
        return None

    
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
        als = AcademyLocationSerializer(
            data=location, 
            context={
                'images': location.get('images'),
                'name': validated_data['name']
            }
        )
        als.is_valid(raise_exception=True)
        location_ = als.save()
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
        return AcademyLocationSerializer(academy.location).data


class AcademyListSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.detail')

    class Meta:
        model = Academy
        fields = (
            'name',
            'location',
            'logo',
            'contact'
        )
