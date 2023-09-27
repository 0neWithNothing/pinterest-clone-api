from rest_framework import generics
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import UserSerializer, ProfileSerializer
from .models import Profile

User = get_user_model()

class UserCreateAPIView(generics.CreateAPIView):
    model = User
    permission_classes = []
    serializer_class = UserSerializer


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    
    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    