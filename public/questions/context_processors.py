from .models import Tag
from django.contrib.auth.models import User
from django.db.models import Count


def popular_tags(request):
    tags = Tag.objects.annotate(questions_count=Count("questions")).order_by(
        "-questions_count"
    )[:8]
    return {"popular_tags": tags}


def best_members(request):
    members = User.objects.annotate(answers_count=Count("answers")).order_by(
        "-answers_count"
    )[:5]
    return {"best_members": members}
