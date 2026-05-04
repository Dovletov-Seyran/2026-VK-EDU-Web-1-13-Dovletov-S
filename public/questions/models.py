from django.db import models
from django.utils import timezone


class Question(models.Model):
    title = models.CharField(max_length=250)
    slug = models.SlugField(max_length=250)
    text = models.TextField()
    user_id = None
    publish_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
