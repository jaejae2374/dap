from rest_framework import serializers
from util.location.models import LocationImage, Location

class LocationImageSerializer(serializers.ModelSerializer):
    class Meta: 
        model = LocationImage
        fields = (
            'id',
            'image'
        )

class LocationSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()

    class Meta:
        model = Location
        fields = (
            'id',
            'type',
            'detail',
            'city',
            'district',
            'description',
            'images'
        )
        extra_kwargs = {
            'detail': {'required': True},
            'type': {'required': True},
        }

    def create(self, validated_data: dict) -> Location:
        # TODO: parsing detail to city, district method.
        location = Location.objects.create(
            type = validated_data['type'],
            detail = validated_data['detail'],
            city = validated_data.get('city'),
            district = validated_data.get('district'),
            description = validated_data.get('description')
        )
        if self.context.get('images'):
            LocationImage.objects.bulk_create(
                [
                    LocationImage(
                        location=location,
                        name=f"{location.type}/{self.context['name']}",
                        image=image
                    ) for image in self.context['images']
                ]
            )
        return location

    def get_images(self, location: Location):
        if location.images:
            return LocationImageSerializer(location.images, many=True).data
        return None
