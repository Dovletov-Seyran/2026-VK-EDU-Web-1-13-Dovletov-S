from django.core.cache import cache
from django.db.models.functions import Coalesce
from django.db.models import Count, Sum, F, Q
from django.utils import timezone
from datetime import timedelta

from .models import Tag
from django.contrib.auth.models import User

from django.conf import settings as django_settings


def popular_tags(request):
    tags = cache.get("popular_tags")

    if tags is None:
        three_months_ago = timezone.now() - timedelta(days=90)

        tags = list(
            Tag.objects.filter(questions__created_at__gte=three_months_ago)
            .annotate(questions_count=Count("questions"))
            .order_by("-questions_count")[:10]
        )

        cache.set("popular_tags", tags, timeout=7200)

    return {"popular_tags": tags}


def best_members(request):
    members = cache.get("best_members")

    if members is None:
        one_week_ago = timezone.now() - timedelta(weeks=1)
        members = list(
            User.objects.annotate(
                questions_rating=Coalesce(
                    Sum(
                        "questions__likes__vote",
                        filter=Q(questions__created_at__gte=one_week_ago),
                    ),
                    0,
                ),
                answers_rating=Coalesce(
                    Sum(
                        "answers__likes__vote",
                        filter=Q(answers__created_at__gte=one_week_ago),
                    ),
                    0,
                ),
            )
            .annotate(total_rating=F("questions_rating") + F("answers_rating"))
            .order_by("-total_rating")[:10]
        )
        cache.set("best_members", members, timeout=7200)

    return {"best_members": members}


def centrifugo_settings(request):
    return {
        "CENTRIFUGO_WS_URL": django_settings.CENTRIFUGO_WS_URL,
    }
