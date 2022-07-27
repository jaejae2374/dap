from rest_framework import status, viewsets, permissions
from user.core.academy.models import Academy
from user.core.academy.serializers import AcademySerializer, AcademyListSerializer
from rest_framework.response import Response

class AcademyViewSet(viewsets.GenericViewSet):
    queryset = Academy.objects.all()
    serializer_class = AcademySerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request):
        """Create academy."""
        data = request.data
        serializer = self.get_serializer(
            data=data,
            context={'location': data.get('location')})
        serializer.is_valid(raise_exception=True)
        academy = serializer.save()
        # TODO: response serializer? too heavy?
        return Response(AcademySerializer(academy).data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """List academy."""
        # TODO: add location keyword search.
        name = request.query_params.get("name")
        location = request.query_params.get("location")
        if name:
            results = Academy.objects.filter(name__icontains=name)
        elif location:
            results = Academy.objects.filter(location__detail__icontains=location).order_by('name')
        else: 
            results = []
        return Response(AcademyListSerializer(results, many=True).data, status=status.HTTP_200_OK)
