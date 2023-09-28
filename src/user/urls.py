from django.urls import path, include

from . import views

urlpatterns = [
    path('register/', views.UserCreateAPIView.as_view(), name='register'),
    path('profile/<slug:slug>/', views.ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
    path('profile/<slug:slug>/follows/', views.FollowAPIView.as_view(), name='follows'),
]