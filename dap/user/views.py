from django.contrib.auth import login, logout
from rest_framework import status, permissions, viewsets, generics
from rest_framework.response import Response
from user.serializers import UserCreateSerializer, UserLoginSerializer, UserRetrieveSerializer, UserUpdateSerializer, MentorSearchSerializer
from user.profile.serializers import MentorSerializer, MenteeSerializer
from dap.errors import FieldError, NotFound
from rest_framework.decorators import action
from user.profile.utils import profile_update
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db import transaction
User = get_user_model()

class UserViewSet(viewsets.GenericViewSet, generics.RetrieveDestroyAPIView):
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
        elif self.action == "mentor":
            return MentorSearchSerializer

    @transaction.atomic()
    def create(self, request):
        """Create User."""
        data = request.data
        if data.get('mentor'):
            mentor_data = data.pop('mentor')
            ms = MentorSerializer(
                data=mentor_data, 
                context={
                    'academies': mentor_data.get('academies'),
                    'genres': mentor_data.get('genres')
                })
            profile_name = 'mentor'
        elif data.get('mentee'):
            mentee_data = data.pop('mentee')
            ms = MenteeSerializer(
                data=mentee_data,
                context={
                    'genres': mentee_data.get('genres')
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

    @transaction.atomic()
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
        return super().retrieve(request, pk)

    def delete(self, request, pk=None):
        """Retrieve User."""
        return super().delete(request, pk)

    @action(methods=['PUT'], detail=False)
    def login(self, request):
        """User Login."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = serializer.validated_data['token']
        return Response({'success': True, 'token': token}, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def logout(self, request):
        """User Logout."""
        request.user.auth_token.delete()
        logout(request)
        return Response(status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False)
    def mentor(self, request):
        """Mentor List/Search"""
        page = request.query_params.get('page', '1')
        name = request.query_params.get('name')
        genre = request.query_params.getlist('genre')
        academy = request.query_params.get('academy')

        mentors = User.objects.filter(mentee=None)
        if name: 
            mentors = mentors.filter(username__icontains=name)
        if genre:
            mentors = mentors.filter(mentor__genre__name__in=genre)
        if academy:
            mentors = mentors.filter(mentor__academy__name__icontains=academy)
        if not (name or genre or academy):
            mentors = []

        results = self.get_serializer(mentors.order_by('username'), many=True).data
        results = Paginator(results, 20).get_page(page)
        return Response(list(results), status=status.HTTP_200_OK)
            

        



