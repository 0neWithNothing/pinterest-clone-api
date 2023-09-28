from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()

router.register(r'boards', views.BoardViewSet, basename='board')
router.register(r'pins', views.PinViewSet, basename='pin')


urlpatterns = [
    path('', include(router.urls)),
    path('pins/<int:pk>/likes/', views.LikeAPIView.as_view(), name='likes'),
    path('pins/<int:pk>/comment/', views.CommentCreateAPIView.as_view(), name='add_comment'),
    path('comments/<int:pk>/', views.CommentRetrieveUpdateDestroy.as_view(), name='comment'),
]