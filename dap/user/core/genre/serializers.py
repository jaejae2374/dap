from rest_framework import serializers
from django.contrib.auth import get_user_model
from user.core.genre.models import Genre
User = get_user_model()

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'id',
            'name',
            'description',
            'video'
        )
