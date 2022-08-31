from rest_framework import status, viewsets, generics
from rest_framework.response import Response
from dap.errors import NotOwner, FieldError, NotFound, DuplicationError
from lesson.permissions import IsOwnerOrReadOnly
from user.permissions import IsMentee
from lesson.lesson.models import Lesson
from lesson.lesson.serializers import LessonCreateSerializer, LessonRetrieveSerializer, LessonListSerializer, LessonSearchSerializer, LessonUpdateSerializer
from rest_framework.decorators import action
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from django.db.models import Q
from django.core.paginator import Paginator
from util.location.utils import set_location
from django.db import transaction


class LessonViewSet(viewsets.GenericViewSet, generics.RetrieveDestroyAPIView):
    queryset = Lesson.objects.all()

    def get_permissions(self):
        # self.check_object_permissions(self.request, user)
        if self.action in ['participate', 'cancel']:
            permission_classes = [IsMentee]
        else:
            permission_classes = [IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

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
        # TODO: 지난 날짜 create 불가
        if not request.user.mentor:
            raise NotOwner("Not allowed.")
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
        return super().delete(request, pk)

    def list(self, request):
        # TODO: 이미 지난 day?
        # TODO: 중복 제거
        page = request.query_params.get('page', '1')
        today = datetime.today()
        month = int(request.query_params.get('month', today.month))
        day = request.query_params.get('day', None)
        genres = request.query_params.getlist('genre')
        city = request.query_params.get('city')

        if not (genres and city):
            raise FieldError("genre or city is empty.")
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

        recruit_number = request.query_params.get('recruit_number', 1)
        max_price = request.query_params.get('max_price')
        min_price = request.query_params.get('min_price')
        academies = request.query_params.getlist('academy')
        mentors = request.query_params.getlist('mentor')
        districts = request.query_params.getlist('district')
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
