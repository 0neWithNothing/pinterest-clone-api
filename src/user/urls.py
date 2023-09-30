from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

urlpatterns = [
    path('auth/register/', views.UserCreateAPIView.as_view(), name='register'),
    path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/logout_token/', views.APILogoutView.as_view(), name='logout_token'),
    path('profile/<slug:slug>/', views.ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('profile/<slug:slug>/follows/', views.FollowAPIView.as_view(), name='follows'),
]