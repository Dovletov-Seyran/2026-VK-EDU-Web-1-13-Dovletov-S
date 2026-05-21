from django.contrib import admin
from .models import Tag, Question, Answer, QuestionLike, AnswerLike


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ["title", "slug"]
    prepopulated_fields = {"slug": ("title",)}


class AnswerInline(admin.StackedInline):
    model = Answer


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]
    list_display = ["title", "user", "publish_at", "created_at"]
    search_fields = ["title", "text"]
    list_filter = ["publish_at", "created_at"]
    prepopulated_fields = {"slug": ("title",)}
    list_select_related = ["user"]
    raw_id_fields = ["user", "tags"]


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ["text", "accepted", "question", "user"]
    search_fields = ["text"]
    list_filter = ["accepted", "created_at"]
    list_select_related = ["question", "user"]
    raw_id_fields = ["question", "user"]


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "question", "created_at"]
    list_filter = ["created_at"]
    list_select_related = ["user", "question"]
    raw_id_fields = ["user", "question"]


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ["user", "answer", "created_at"]
    list_filter = ["created_at"]
    list_select_related = ["user", "answer"]
    raw_id_fields = ["user", "answer"]
