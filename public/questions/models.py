from django.contrib.auth.models import User
from django.db import models
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.urls import reverse
from django.contrib.postgres.indexes import GinIndex

LIKE = 1
DISLIKE = -1
VOTE_CHOICES = [
    (LIKE, "Лайк"),
    (DISLIKE, "Дизлайк"),
]


class QuestionManager(models.Manager):
    def _with_rating(self):
        return self.annotate(likes_count=Coalesce(Sum("likes__vote"), 0))

    def new(self):
        return self._with_rating().order_by("-created_at")

    def best(self):
        return self._with_rating().order_by("-likes_count")


class Tag(models.Model):
    title = models.CharField(max_length=255, unique=True, verbose_name="Название тега")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Слаг")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"

    def __str__(self):
        return self.title


class Question(models.Model):
    title = models.CharField(max_length=255, verbose_name="Заголовок вопроса")
    slug = models.SlugField(max_length=255, unique=True, verbose_name="Слаг")
    text = models.TextField(verbose_name="Текст вопроса")
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="questions", verbose_name="Автор"
    )
    tags = models.ManyToManyField(
        Tag, related_name="questions", blank=True, verbose_name="Теги"
    )
    publish_at = models.DateTimeField(
        default=timezone.now, verbose_name="Дата публикации"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    objects = QuestionManager()

    class Meta:
        verbose_name = "Вопрос"
        verbose_name_plural = "Вопросы"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("questions:question", kwargs={"question_id": self.id})


class Answer(models.Model):
    text = models.TextField(verbose_name="Текст ответа")
    accepted = models.BooleanField(default=False, verbose_name="Принят")
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Вопрос",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name="Пользователь",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Ответ"
        verbose_name_plural = "Ответы"

    def __str__(self):
        return f'Answer by {self.user.username} on "{self.question.title}"'


class QuestionLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="question_likes",
        verbose_name="Пользователь",
    )
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name="likes", verbose_name="Вопрос"
    )
    vote = models.SmallIntegerField(choices=VOTE_CHOICES, verbose_name="Голос")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        unique_together = ("user", "question")
        verbose_name = "Лайк вопроса"
        verbose_name_plural = "Лайки вопросов"

    def __str__(self):
        return f'{self.user.username} liked question "{self.question.title}"'


class AnswerLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="answer_likes",
        verbose_name="Пользователь",
    )

    answer = models.ForeignKey(
        Answer, on_delete=models.CASCADE, related_name="likes", verbose_name="Ответ"
    )

    vote = models.SmallIntegerField(choices=VOTE_CHOICES, verbose_name="Голос")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        unique_together = ("user", "answer")
        verbose_name = "Лайк ответа"
        verbose_name_plural = "Лайки ответов"

    def __str__(self):
        return f"{self.user.username} liked answer {self.answer.id}"
