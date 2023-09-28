from rest_framework import generics
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import UserSerializer, ProfileSerializer, UserFollowingSerializer
from .models import Profile, UserFollowing

User = get_user_model()

class UserCreateAPIView(generics.CreateAPIView):
    model = User
    permission_classes = []
    serializer_class = UserSerializer


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = 'slug'
    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)


class FollowAPIView(APIView):
    def post(self, request, slug):
        following_user = get_object_or_404(User, profile__slug=slug)
        if following_user == request.user:
            return Response({'detail': 'You can\'t follow on yourself'}, status=status.HTTP_400_BAD_REQUEST)
        user_follow, created = UserFollowing.objects.get_or_create(user=request.user, following_user=following_user)
        if created:
            serializer = UserFollowingSerializer(user_follow)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        user_follow.delete()
        return Response(status=status.HTTP_200_OK)
    