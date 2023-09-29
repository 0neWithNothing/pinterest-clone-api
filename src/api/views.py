from rest_framework import viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import DestroyModelMixin
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Board, Pin, Comment, Like
from .serializers import BoardSerializer, PinSerializer, PinCreateSerializer, PinRetrieveSerializer, LikeSerializer, CommentSerializer
from .permissions import IsOwnerOrReadOnly


class BoardViewSet(viewsets.ModelViewSet):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class PinViewSet(viewsets.ModelViewSet):
    queryset = Pin.objects.all()
    permission_classes = [IsOwnerOrReadOnly]

    def get_queryset(self):
        return Pin.objects.annotate(total_likes=Count('likes'), total_comments=Count('comments'))

    def get_serializer_class(self):
        if self.action == 'create':
            return PinCreateSerializer
        if self.action == 'retrieve':
            return PinRetrieveSerializer
        return PinSerializer

    def perform_create(self, serializer):
        serializer.save(
            user=self.request.user
        )


class LikeAPIView(DestroyModelMixin, generics.ListCreateAPIView):
    serializer_class = LikeSerializer

    def get_pin(self):
        pin = get_object_or_404(Pin, pk=self.kwargs.get(self.lookup_field))
        return pin

    def get_queryset(self):
        likes_qs = Like.objects.filter(pin=self.get_pin())
        return likes_qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if self.get_queryset().filter(user=request.user).exists():
            return Response({'detail': 'You have already liked the pin'}, status=status.HTTP_400_BAD_REQUEST)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(
            pin=self.get_pin(),
            user=self.request.user,
        )

    def get_object(self):
        like = get_object_or_404(Like, pin=self.get_pin(), user=self.request.user)
        return like
    
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


class CommentCreateAPIView(generics.CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        pin = Pin.objects.get(pk=self.kwargs.get("pk"))
        serializer.save(
            pin=pin,
            user=self.request.user
        )
    

class CommentRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer