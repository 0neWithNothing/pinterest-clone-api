from django.db import models
from django.contrib.auth import get_user_model
from .utils import RandomFileName

User = get_user_model()


class Board(models.Model):
    user = models.ForeignKey(User, related_name='boards', on_delete=models.CASCADE)
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self) -> str:
        return self.title


class Pin(models.Model):
    user = models.ForeignKey(User, related_name='pins', on_delete=models.CASCADE)
    board = models.ForeignKey(Board, related_name='pins', null=True, on_delete=models.SET_NULL)
    image = models.ImageField(upload_to=RandomFileName('pins'))
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title


class Comment(models.Model):
    pin = models.ForeignKey(Pin, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='comments', on_delete=models.CASCADE)
    content = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Like(models.Model):
    pin = models.ForeignKey(Pin, related_name='likes', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='likes', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['pin','user'],  name="unique_like")
        ]
