from django.contrib.auth.models import User
from django.db import models
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated

from simplify_rest_framework.views import ModelFactory, register


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username


def create_user(self, data):
    user = User.objects.create_user(**data)
    user.set_password(data['password'])
    user.save()
    return user


@register(User)
class UserFactory(ModelFactory):
    fields = ['username', 'first_name', 'last_name', 'email', 'password']
    write_only_fields = ['password']
    create_instance = create_user


def get_obj(self1, self2):
    return get_object_or_404(UserProfile, user=self2.request.user)


@register(UserProfile)
class UserProfileFactory(ModelFactory):
    auto_user_field = 'user'
    disabled_actions = ['list']
    readonly_fields = ['user']
    get_object = get_obj
    permission_classes = [IsAuthenticated]
