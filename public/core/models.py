import os
import uuid

from django.contrib.auth.models import User
from django.db import models
from django.contrib.staticfiles.storage import staticfiles_storage


def avatar_upload_to(instance, filename):
    ext = os.path.splitext(filename)[1].lower()
    new_filename = f"{uuid.uuid4()}{ext}"
    return f"avatar/{new_filename}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="Пользователь",
    )
    avatar = models.ImageField(
        upload_to=avatar_upload_to, blank=True, null=True, verbose_name="Аватарка"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    @property
    def avatar_url(self):
        if self.avatar:
            return self.avatar.url
        return staticfiles_storage.url("images/default_ava.jpg")

    def __str__(self):
        return self.user.username
