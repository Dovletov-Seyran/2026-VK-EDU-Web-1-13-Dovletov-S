from celery import shared_task
from django.core.cache import cache
from django.db.models import Count, Sum, F, Q
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from .models import Tag
from django.contrib.auth.models import User
import requests
import json
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def update_popular_tags_cache():
    three_months_ago = timezone.now() - timedelta(days=90)

    tags = list(
        Tag.objects.filter(questions__created_at__gte=three_months_ago)
        .annotate(questions_count=Count("questions"))
        .order_by("-questions_count")[:10]
    )

    cache.set("popular_tags", tags, timeout=7200)
    return f"Updated popular_tags: {len(tags)} tags"


@shared_task
def update_best_members_cache():
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
    return f"Updated best_members: {len(members)} members"


@shared_task
def notify_new_answer(question_id, answer_data):
    channel = f"questions:question_{question_id}"

    response = requests.post(
        settings.CENTRIFUGO_API_URL,
        json={
            "method": "publish",
            "params": {
                "channel": channel,
                "data": answer_data,
            },
        },
        headers={
            "Content-Type": "application/json",
            "Authorization": f"apikey {settings.CENTRIFUGO_API_KEY}",
        },
    )

    return f"Centrifugo response: {response.status_code}"


@shared_task
def send_new_answer_email(
    question_title, question_id, question_author_email, answer_username
):
    send_mail(
        subject=f'Новый ответ на ваш вопрос: "{question_title}"',
        message=(
            f"Пользователь {answer_username} ответил на ваш вопрос.\n"
            f"Посмтреть: http://localhost:8000/question/{question_id}/"
        ),
        from_email=None,
        recipient_list=[question_author_email],
    )

    return f"Email sent to {question_author_email}"
