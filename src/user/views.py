from rest_framework import generics
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .serializers import UserSerializer, ProfileSerializer, UserFollowingSerializer
from .models import Profile, UserFollowing
from api.permissions import IsOwnerOrReadOnly

User = get_user_model()

class UserCreateAPIView(generics.CreateAPIView):
    model = User
    serializer_class = UserSerializer


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all().prefetch_related('user__boards')
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'slug'

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class FollowAPIView(DestroyModelMixin, generics.ListCreateAPIView):
    serializer_class = UserFollowingSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'slug'

    def get_user(self):
        user = get_object_or_404(User, profile__slug=self.kwargs.get(self.lookup_field))
        return user

    def get_queryset(self):
        followers = self.get_user().followers.all()
        return followers

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.get_queryset().filter(user=request.user).exists():
            return Response({'detail': 'You have already followed to this user'}, status=status.HTTP_400_BAD_REQUEST)
        if self.get_user() == request.user:
            return Response({'detail': 'You can\'t follow to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user,
            following_user=self.get_user(),
        )

    def get_object(self):
        user_follow = get_object_or_404(UserFollowing, user=self.request.user, following_user=self.get_user())
        return user_follow
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    