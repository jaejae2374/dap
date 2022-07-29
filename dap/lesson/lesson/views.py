from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from lesson.lesson.models import Lesson
from lesson.lesson.serializers import LessonCreateSerializer, LessonRetrieveSerializer
from rest_framework.decorators import action

class LessonViewSet(viewsets.GenericViewSet, generics.RetrieveDestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return LessonCreateSerializer
        elif self.action == "retrieve":
            return LessonRetrieveSerializer
        
    def create(self, request):
        data = request.data
        serializer = self.get_serializer(
            data=data,
            context={
                'location': data.get('location'),
                'genres': data.get('genres'),
                'mentors': data.get('mentors')
            }
        )
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        return Response(self.get_serializer(lesson).data, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        pass

    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk)

    def delete(self, request, pk=None):
        return super().delete(request, pk)

