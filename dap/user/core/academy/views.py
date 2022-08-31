from rest_framework import status, viewsets
from rest_framework.permissions import AllowAny
from user.permissions import IsMentor
from user.core.academy.models import Academy
from user.core.academy.serializers import AcademySerializer, AcademyListSerializer
from rest_framework.response import Response
from django.core.paginator import Paginator
from django.db import transaction

class AcademyViewSet(viewsets.GenericViewSet):
    queryset = Academy.objects.all()
    serializer_class = AcademySerializer
    permission_classes = [AllowAny]

    def get_permissions(self):
        # self.check_object_permissions(self.request, user)
        if self.action in ['create']:
            permission_classes = [IsMentor]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    @transaction.atomic()
    def create(self, request):
        """Create academy."""
        data = request.data
        serializer = self.get_serializer(
            data=data,
            context={
                'location': data.get('location'),
                'genres': data.get('genres'),
                'mentors': data.get('mentors')})
        serializer.is_valid(raise_exception=True)
        academy = serializer.save()
        # TODO: response serializer? too heavy?
        return Response(AcademySerializer(academy).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """List academy."""
        page = request.query_params.get('page', '1')
        name = request.query_params.get("name")
        location = request.query_params.get("location")
        if name:
            results = Academy.objects.filter(name__icontains=name)
        elif location:
            results = Academy.objects.filter(location__detail__icontains=location).order_by('name')
        else: 
            results = []
        results = Paginator(results, 20).get_page(page)
        return Response(AcademyListSerializer(results, many=True).data, status=status.HTTP_200_OK)
