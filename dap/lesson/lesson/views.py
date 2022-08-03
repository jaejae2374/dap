from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from dap.errors import NotAllowed, FieldError
from lesson.lesson.models import Lesson
from lesson.lesson.serializers import LessonCreateSerializer, LessonRetrieveSerializer, LessonListSerializer
from rest_framework.decorators import action
from datetime import datetime
from dateutil.relativedelta import relativedelta

class LessonViewSet(viewsets.GenericViewSet, generics.RetrieveDestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return LessonCreateSerializer
        elif self.action == "retrieve":
            return LessonRetrieveSerializer
        elif self.action == "list":
            return LessonListSerializer
        
    def create(self, request):
        # TODO: custom permission such as MentorOnly
        if not request.user.mentor:
            raise NotAllowed("only mentor can create lesson.")
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
        return Response({"id": lesson.id, "status": "success"}, status=status.HTTP_201_CREATED)

    def update(self, request, pk=None):
        pass

    def retrieve(self, request, pk=None):
        # TODO: user, academy serializer 간소화
        return super().retrieve(request, pk)

    def delete(self, request, pk=None):
        return super().delete(request, pk)

    def list(self, request):
        today = datetime.today()
        month = int(request.query_params.get('month', today.month))
        day = request.query_params.get('day', None)
        genres = request.query_params.getlist('genres')
        city = request.query_params.get('city')

        if not (genres and city):
            raise FieldError("genres or city is empty.")
        if day:
            day=int(day)
            if day == today.day:
                start = datetime.now()
            else:
                start = datetime(
                    year=2022, 
                    month=month, 
                    day=day,
                    hour=0,
                    minute=0,
                    second=0)
            end = datetime(
                year=2022, 
                month=month, 
                day=(start+relativedelta(days=1)).day, 
                hour=0, 
                minute=0, 
                second=0)
        else:
            start = datetime.now()
            end = datetime(
                year=2022, 
                month=(start+relativedelta(months=1)).month, 
                day=1, 
                hour=0, 
                minute=0, 
                second=0)
        
        results = Lesson.objects.filter(
            started_at__gte=start, 
            finished_at__lt=end,
            genre__in=genres,
            location__city=city)

        recruit_number = request.query_params.get('recruit_number')
        max_price = request.query_params.get('max_price')
        min_price = request.query_params.get('min_price')
        academies = request.query_params.getlist('academies')
        mentors = request.query_params.getlist('mentors')
        districts = request.query_params.getlist('districts')
        if recruit_number:
            results = results.filter(recruit_number__gte=recruit_number)
        if min_price:
            results = results.filter(price__gte=min_price)
        if max_price:
            results = results.filter(price__lte=max_price)
        if academies:
            results = results.filter(academy__in=academies)
        if mentors:
            results = results.filter(mentor__in=mentors)
        if districts:
            results = results.filter(location__district__in=districts)

        return Response(self.get_serializer(results, many=True).data, status=status.HTTP_200_OK)
