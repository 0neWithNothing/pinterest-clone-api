import os
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save, post_delete
from django.dispatch import receiver

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

@receiver(post_delete, sender=Pin)
def pin_delete_image_on_delete(sender, instance, **kwargs):
    """
    Deletes image from filesystem
    when corresponding `Pin` object is deleted.
    """
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)

@receiver(pre_save, sender=Pin)
def pin_delete_image_on_change(sender, instance, **kwargs):
    """
    Deletes old image from filesystem
    when corresponding `Pin` object is updated
    with new image.
    """
    if not instance.pk:
        return False
    try:
        old_image = Pin.objects.get(pk=instance.pk).image
    except Pin.DoesNotExist:
        return False
    if not old_image:
        return False
    new_image = instance.image
    if not old_image == new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)