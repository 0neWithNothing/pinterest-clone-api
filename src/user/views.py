from rest_framework import generics
from django.contrib.auth import get_user_model

from .serializers import UserSerializer

User = get_user_model()

class UserCreateAPIView(generics.CreateAPIView):
    model = User
    permission_classes = []
    serializer_class = UserSerializer
