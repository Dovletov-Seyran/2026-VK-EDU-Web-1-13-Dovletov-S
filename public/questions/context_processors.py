from .models import Tag, Question


def popular_tags(request):
    tags = Tag.objects.all()[:8]
    return {"popular_tags": tags}


def best_members(request):
    from django.contrib.auth.models import User

    members = User.objects.order_by("-id")[:5]
    return {"best_members": members}
