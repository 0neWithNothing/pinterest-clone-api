from rest_framework import viewsets
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db.models import Count

from .models import Board, Pin, Comment, Like
from .serializers import BoardSerializer, PinSerializer, PinCreateSerializer, PinRetrieveSerializer, LikeSerializer, CommentSerializer


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
    permission_classes = []

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


class LikeAPIView(APIView):
    def post(self, request, pk):
        pin = get_object_or_404(Pin, pk=pk)
        like, created = Like.objects.get_or_create(pin=pin, user=request.user)
        if created:
            serializer = LikeSerializer(like)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        like.delete()
        return Response(status=status.HTTP_200_OK)


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