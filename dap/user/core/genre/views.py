from rest_framework import status, viewsets, generics
from rest_framework.permissions import AllowAny
from user.core.genre.models import Genre
from user.core.genre.serializers import GenreSerializer
from user.permissions import IsAdminUser
from rest_framework.response import Response
from django.db import transaction

class GenreViewSet(viewsets.GenericViewSet, generics.RetrieveUpdateDestroyAPIView):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer

    def get_permissions(self):
        # self.check_object_permissions(self.request, user)
        if self.action in ['create']:
            permission_classes = [IsAdminUser]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @transaction.atomic()
    def create(self, request):
        """Create genre."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        genre = serializer.save()
        return Response(self.get_serializer(genre).data, status=status.HTTP_201_CREATED)


    def list(self, request):
        """List genre."""
        name = request.query_params.get("name")
        if name:
            results = Genre.objects.filter(name__icontains=name)
        else: 
            results = []
        return Response(self.get_serializer(results, many=True).data, status=status.HTTP_200_OK)
