from django.urls import path, include

from . import views

urlpatterns = [
    path('register/', views.UserCreateAPIView.as_view(), name='register'),
    path('profile/<int:pk>/', views.ProfileRetrieveUpdateAPIView.as_view(), name='profile'),
]