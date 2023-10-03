import os
from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from api.utils import RandomFileName
from django.template.defaultfilters import slugify


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(
            email = self.normalize_email(email),
        )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password=password)
        user.is_superuser = True
        user.is_staff = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()
    email = models.EmailField(unique=True, db_index=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    ordering = ('created',)


    def get_full_name(self):
        return self.email
    
    def get_short_name(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(User, related_name='profile', on_delete=models.CASCADE)
    username = models.CharField(unique=True, max_length=20)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    bio = models.TextField(blank=True)
    avatar = models.ImageField(upload_to=RandomFileName('profile_pics'), null=True, blank=True)
    slug = models.SlugField()

    def __str__(self) -> str:
        return self.username


class UserFollowing(models.Model):

    user = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    following_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user','following_user'],  name="unique_followers")
        ]

        ordering = ['-created']

    def __str__(self):
        return f"{self.user} follows {self.following_user}"


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        username = instance.email.split('@')[0]
        Profile.objects.create(user=instance, username=username, slug=slugify(username))


@receiver(post_delete, sender=Profile)
def profile_delete_image_on_delete(sender, instance, **kwargs):
    """
    Deletes image from filesystem
    when corresponding `Profile` object is deleted.
    """
    if instance.avatar:
        if os.path.isfile(instance.avatar.path):
            os.remove(instance.avatar.path)

@receiver(pre_save, sender=Profile)
def profile_delete_image_on_change(sender, instance, **kwargs):
    """
    Deletes old image from filesystem
    when corresponding `Profile` object is updated
    with new image.
    """
    if not instance.pk:
        return False
    try:
        old_image = Profile.objects.get(pk=instance.pk).avatar
    except Profile.DoesNotExist:
        return False
    if not old_image:
        return False
    new_image = instance.avatar
    if not old_image == new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)