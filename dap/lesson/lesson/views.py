from rest_framework import status, viewsets, permissions, generics
from rest_framework.response import Response
from dap.errors import NotAllowed, FieldError, NotFound, DuplicationError
from lesson.lesson.models import Lesson
from lesson.lesson.serializers import LessonCreateSerializer, LessonRetrieveSerializer, LessonListSerializer, LessonSearchSerializer, LessonUpdateSerializer
from rest_framework.decorators import action
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.core.paginator import Paginator
from util.location.utils import set_location
from django.db import transaction
import pytz 
utc=pytz.UTC

class LessonViewSet(viewsets.GenericViewSet, generics.RetrieveDestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == "create":
            return LessonCreateSerializer
        elif self.action in ["retrieve", "participate"]:
            return LessonRetrieveSerializer
        elif self.action == "list":
            return LessonListSerializer
        elif self.action == "search":
            return LessonSearchSerializer
        elif self.action == "update":
            return LessonUpdateSerializer
    
    @transaction.atomic()
    def create(self, request):
        # TODO: custom permission such as MentorOnly
        if not request.user.mentor:
            raise NotAllowed("Only mentor can create lesson.")
        data = request.data
        serializer = self.get_serializer(
            data=data,
            context={
                'location': data.get('location'),
                'mentors': data.get('mentors')
            }
        )
        serializer.is_valid(raise_exception=True)
        lesson = serializer.save()
        return Response({"id": lesson.id, "status": "success"}, status=status.HTTP_201_CREATED)

    @transaction.atomic()
    def update(self, request, pk=None):
        # TODO: Only the lesson mentor can update it.
        try:
            data = request.data
            mentors = data.get("mentors")
            mentees = data.get("mentees")
            genres = data.get("genres")
            location = data.get("location")
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            raise NotFound("Lesson does not exists.")
        if mentors: lesson.mentor.set(mentors)
        if mentees: lesson.mentee.set(mentees)
        if genres: lesson.genre.set(genres)
        if location: 
            _location = set_location(data=data, type="lesson", name=str(lesson.id))
            data['location'] = _location.id
        serializer = self.get_serializer(lesson, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"id": lesson.id, "status": "success"}, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        return super().retrieve(request, pk)

    def delete(self, request, pk=None):
        # TODO: Only the lesson mentor can update it.
        return super().delete(request, pk)

    def list(self, request):
        page = request.query_params.get('page', '1')
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

        results = Paginator(results, 20).get_page(page)
        return Response(self.get_serializer(results, many=True).data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=True)
    def participate(self, request, pk=None):
        # TODO: 결제 기능 연동
        user = request.user
        if not user.mentee:
            raise NotAllowed("Only mentee can participate lesson.")
        now = datetime.now()
        try:
            lesson = Lesson.objects.get(pk=pk)
            if user.classes.filter(id=pk).exists():
                raise DuplicationError("Already participated.")
            if lesson.started_at <= now:
                raise FieldError("Lesson overdue.")
            if not (lesson.recruit_number > 0):
                raise FieldError("Lesson overcrowded.")
        except Lesson.DoesNotExist:
            raise NotFound("Lesson does not exist.")
        lesson.recruit_number-=1
        lesson.mentee.add(user)
        lesson.save()
        user.mentee.courses_count+=1
        user.mentee.save()
        return Response(self.get_serializer(lesson).data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False)
    def search(self, request):
        # TODO: results 중복 제거
        page = request.query_params.get('page', '1')
        keyword = request.query_params.get('keyword', None)
        past = request.query_params.get('past', False)
        now = datetime.now()
        results = []
        if keyword:
            results = Lesson.objects.filter(
                Q(title__icontains=keyword) |\
                Q(description__icontains=keyword) |\
                Q(academy__name__icontains=keyword) |\
                Q(mentor__username__icontains=keyword)
            )
            if not past:
                results = results.filter(finished_at__gt=now)
            results = results.order_by("-started_at")
        results = Paginator(results, 20).get_page(page)
        return Response(self.get_serializer(results, many=True).data, status=status.HTTP_200_OK)

    @action(methods=["PUT"], detail=True)
    def cancel(self, request, pk=None):
        std = (datetime.now() + timedelta(minutes=30))
        user = request.user
        if not user.mentee:
            raise NotAllowed("Only mentee can cancel lesson.")
        try:
            lesson = Lesson.objects.get(pk=pk)
            if not user.classes.filter(id=pk).exists():
                raise NotFound("Not participated.")
            if lesson.started_at <= std:
                raise FieldError("Cancel overdue.")
        except Lesson.DoesNotExist:
            raise NotFound("Lesson does not exist.")
        lesson.mentee.remove(user)
        lesson.recruit_number+=1
        lesson.save()
        user.mentee.courses_count-=1
        user.mentee.save()
        return Response("Successfully Canceled.", status=status.HTTP_200_OK)
