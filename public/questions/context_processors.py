from .models import Tag
from django.contrib.auth.models import User


def popular_tags(request):
    tags = Tag.objects.all()[:8]
    return {"popular_tags": tags}


def best_members(request):

    members = User.objects.order_by("-id")[:5]
    return {"best_members": members}
