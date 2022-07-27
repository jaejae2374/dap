from http.client import ResponseNotReady
from django.contrib.auth import login, logout
from rest_framework import status, permissions, viewsets
from rest_framework.response import Response
from user.serializers import UserCreateSerializer, UserLoginSerializer, UserRetrieveSerializer, UserUpdateSerializer
from user.profile.serializers import MentorSerializer, MenteeSerializer
from dap.errors import FieldError, NotFound
from user.core.genre.const import DEFAULT
from rest_framework.decorators import action
from user.profile.utils import profile_update
from django.contrib.auth import get_user_model
User = get_user_model()


class UserView(viewsets.GenericViewSet):
    """User API View."""
    # TODO: permission details.
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == "create":
            return UserCreateSerializer
        elif self.action == "retrieve":
            return UserRetrieveSerializer
        elif self.action == "login":
            return UserLoginSerializer
        elif self.action == "update":
            return UserUpdateSerializer

    def create(self, request):
        """Create User."""
        data = request.data
        if data.get('mentor'):
            mentor_data = data.pop('mentor')
            ms = MentorSerializer(
                data=mentor_data, 
                context={
                    'academies': mentor_data.get('academies'),
                    'genres': mentor_data.get('genres', [DEFAULT])
                })
            profile_name = 'mentor'
        elif data.get('mentee'):
            mentee_data = data.pop('mentee')
            ms = MenteeSerializer(
                data=mentee_data,
                context={
                    'genres': mentee_data.get('genres', [DEFAULT])
                })
            profile_name = 'mentee'
        else: 
            raise FieldError("choose one between mentor, mentee.")
        ms.is_valid(raise_exception=True)
        profile = ms.save()
        data[profile_name] = profile.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        user, token = serializer.save()
        login(request, user)

        return Response({'user': user.id, 'token': token}, status=status.HTTP_201_CREATED)


    def update(self, request, pk=None):
        """Update User."""
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User does not exist.")
        data = request.data
        if data.get('mentor'):
            mentor_data = data.pop('mentor')
            profile_update(user, "mentor", mentor_data)
        elif data.get('mentee'):
            mentee_data = data.pop('mentee')
            profile_update(user, "mentee", mentee_data)
        serializer = self.get_serializer(user, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)

    
    def retrieve(self, request, pk=None):
        """Retrieve User."""
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            raise NotFound("User does not exist.")
        return Response(self.get_serializer(user).data, status=status.HTTP_200_OK)


    @action(methods=['PUT'], detail=False)
    def login(self, request):
        """User Login."""
        serializer = self.get_serializer(data=request.data)
        token = serializer.is_valid(raise_exception=True)

        return Response({'success': True, 'token': token}, status=status.HTTP_200_OK)


