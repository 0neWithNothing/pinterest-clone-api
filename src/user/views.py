from rest_framework import generics
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.contrib.auth import login, logout
from drf_spectacular.utils import extend_schema
from django.core.mail import EmailMessage
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.urls import reverse_lazy

from .token import email_verification_token
from .serializers import UserSerializer, ProfileSerializer, UserFollowingSerializer, LoginSerializer
from .models import Profile, UserFollowing
from api.permissions import IsOwnerOrReadOnly


User = get_user_model()


class UserCreateAPIView(generics.CreateAPIView):
    model = User
    serializer_class = UserSerializer

    def _send_email_verification(self, user):
        domain = settings.BASE_BACKEND_URL
        subject = 'Activate Your Account'
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = email_verification_token.make_token(user)
        activate_uri = reverse_lazy('activate', kwargs={'uidb64':uid, 'token':token})
        body_text = f'Hello, click on the link to confirm your registration'
        body_url = f'{domain}{activate_uri}'
        body = body_text + '\n' + body_url
        EmailMessage(to=[user.email], subject=subject, body=body).send()

    def perform_create(self, serializer):
        user = serializer.save()
        self._send_email_verification(user)


class UserActivateAPIView(APIView):

    def get_user_from_email_verification_token(self, uidb64, token):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return None

        if user is not None and email_verification_token.check_token(user, token):
            return user
        return None

    def get(self, request, uidb64, token):
        user = self.get_user_from_email_verification_token(uidb64, token)
        if user is not None:
            user.is_active = True
            user.save()
            login(request, user)
            return Response({'detail': 'Your account has been successfully verified'}, status=status.HTTP_200_OK)
        return Response({'detail': 'Something went wrong'}, status=status.HTTP_400_BAD_REQUEST)


class LoginViewAPIView(APIView):
    @extend_schema(
        request=LoginSerializer,
        responses={200: LoginSerializer},
    )
    def post(self, request):
        serializer = LoginSerializer(data=self.request.data, context={ 'request': self.request })
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return Response({'detail': 'Successfully logged in'}, status=status.HTTP_200_OK)


class LogoutViewAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({'detail': 'Successfully logged out'}, status=status.HTTP_200_OK)


class ProfileRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    queryset = Profile.objects.all().prefetch_related('user__boards')
    serializer_class = ProfileSerializer
    permission_classes = [IsOwnerOrReadOnly]
    lookup_field = 'slug'


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
    