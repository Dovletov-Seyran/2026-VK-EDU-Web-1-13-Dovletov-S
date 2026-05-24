from django.views.generic import ListView, DetailView, FormView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Question, Tag, QuestionLike, AnswerLike, Answer, LIKE, DISLIKE
from .forms import QuestionForm, AnswerForm
from .utils import paginate

from django.contrib.auth.models import User

from django.db.models import Sum, Q
from django.db.models.functions import Coalesce

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
import json

from .tasks import notify_new_answer, send_new_answer_email

import jwt
import time
from django.conf import settings

from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank


class IndexView(ListView):
    template_name = "questions/index.html"
    context_object_name = "questions"
    paginate_by = 5

    def get_queryset(self):
        return Question.objects.new().prefetch_related("tags").select_related("user")


class HotView(ListView):
    template_name = "questions/hot.html"
    context_object_name = "questions"
    paginate_by = 5

    def get_queryset(self):
        return Question.objects.best().prefetch_related("tags").select_related("user")


class TagView(ListView):
    template_name = "questions/tag.html"
    context_object_name = "questions"
    paginate_by = 5

    def get_queryset(self):
        self.tag = get_object_or_404(Tag, slug=self.kwargs["tag_name"])
        return (
            self.tag.questions.annotate(likes_count=Coalesce(Sum("likes__vote"), 0))
            .order_by("-created_at")
            .prefetch_related("tags")
            .select_related("user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


class AskView(LoginRequiredMixin, FormView):
    template_name = "questions/ask.html"
    form_class = QuestionForm
    login_url = "/login/"

    def form_valid(self, form):
        question = form.save(user=self.request.user)
        return redirect("questions:question", question_id=question.id)


class QuestionView(View):
    def get_question(self, question_id):
        return get_object_or_404(
            Question.objects.annotate(likes_count=Coalesce(Sum("likes__vote"), 0))
            .prefetch_related("tags")
            .select_related("user"),
            id=question_id,
        )

    def get_context(self, question, form, request):
        answers = (
            question.answers.select_related("user")
            .annotate(likes_count=Coalesce(Sum("likes__vote"), 0))
            .order_by("-created_at")
        )
        page = paginate(answers, request)
        return {
            "question": question,
            "page_answer": page.object_list,
            "page": page,
            "form": form,
        }

    def get(self, request, question_id):
        question = self.get_question(question_id)
        form = AnswerForm()
        context = self.get_context(question, form, request)
        return render(request, "questions/question.html", context)

    def post(self, request, question_id):
        question = self.get_question(question_id)

        if not request.user.is_authenticated:
            return redirect(f"/login/?next=/question/{question_id}/")

        form = AnswerForm(request.POST)
        if form.is_valid():
            answer = form.save(user=request.user, question=question)

            # Отправляем уведомление в Centrifugo через Celery
            notify_new_answer.delay(
                question_id=question.id,
                answer_data={
                    "answer_id": answer.id,
                    "text": answer.text,
                    "username": request.user.username,
                    "avatar_url": request.user.profile.avatar_url,
                    "created_at": answer.created_at.isoformat(),
                },
            )

            if question.user.email:
                send_new_answer_email.delay(
                    question_title=question.title,
                    question_id=question.id,
                    question_author_email=question.user.email,
                    answer_username=request.user.username,
                )

            answers = (
                question.answers.select_related("user")
                .annotate(likes_count=Coalesce(Sum("likes__vote"), 0))
                .order_by("-created_at")
            )
            answers_ids = list(answers.values_list("id", flat=True))
            per_page = 5
            try:
                answer_index = answers_ids.index(answer.id)
            except ValueError:
                answer_index = 0
            page_num = (answer_index // per_page) + 1
            return redirect(
                f"/question/{question_id}/?page={page_num}#answer-{answer.id}"
            )

        context = self.get_context(question, form, request)
        return render(request, "questions/question.html", context)


class UserView(ListView):
    template_name = "questions/user.html"
    context_object_name = "questions"
    paginate_by = 5

    def get_queryset(self):
        self.profile_user = get_object_or_404(User, username=self.kwargs["username"])
        return (
            Question.objects.filter(user=self.profile_user)
            .annotate(likes_count=Coalesce(Sum("likes__vote"), 0))
            .order_by("-created_at")
            .prefetch_related("tags")
            .select_related("user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = self.profile_user
        return context


@login_required
@require_POST
def question_vote(request):
    try:
        data = json.loads(request.body)
        question_id = data.get("question_id")
        vote = data.get("vote")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Невалидные данные"}, status=400)

    if vote not in (LIKE, DISLIKE):
        return JsonResponse({"error": "Неверный тип голоса"}, status=400)

    try:
        question = Question.objects.get(id=question_id)
    except Question.DoesNotExist:
        return JsonResponse({"error": "Вопрос не найден"}, status=404)

    user_vote = 0

    try:
        like = QuestionLike.objects.get(user=request.user, question=question)
        if like.vote == vote:
            user_vote = vote
        else:
            like.delete()
            user_vote = 0
    except QuestionLike.DoesNotExist:
        QuestionLike.objects.create(user=request.user, question=question, vote=vote)
        user_vote = vote

    rating = QuestionLike.objects.filter(question=question).aggregate(
        total=Coalesce(Sum("vote"), 0)
    )["total"]

    return JsonResponse({"rating": rating, "user_vote": user_vote})


@login_required
@require_POST
def answer_vote(request):
    try:
        data = json.loads(request.body)
        answer_id = data.get("answer_id")
        vote = data.get("vote")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Невалидные данные"}, status=400)

    if vote not in (LIKE, DISLIKE):
        return JsonResponse({"error": "Неверный тип голоса"}, status=400)

    try:
        answer = Answer.objects.get(id=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({"error": "Ответ не найден"}, status=404)

    user_vote = 0

    try:
        like = AnswerLike.objects.get(user=request.user, answer=answer)
        if like.vote == vote:
            user_vote = vote
        else:
            like.delete()
            user_vote = 0
    except AnswerLike.DoesNotExist:
        AnswerLike.objects.create(user=request.user, answer=answer, vote=vote)
        user_vote = vote

    rating = AnswerLike.objects.filter(answer=answer).aggregate(
        total=Coalesce(Sum("vote"), 0)
    )["total"]

    return JsonResponse({"rating": rating, "user_vote": user_vote})


@login_required
@require_POST
def accept_answer(request):
    try:
        data = json.loads(request.body)
        answer_id = data.get("answer_id")
    except (json.JSONDecodeError, KeyError):
        return JsonResponse({"error": "Невалидные данные"}, status=400)

    try:
        answer = Answer.objects.select_related("question").get(id=answer_id)
    except Answer.DoesNotExist:
        return JsonResponse({"error": "Ответ не найден"}, status=404)

    if answer.question.user != request.user:
        return JsonResponse(
            {"error": "Только автор вопроса может выбирать правильный ответ"},
            status=403,
        )

    if answer.accepted:
        answer.accepted = False
        answer.save()
    else:
        Answer.objects.filter(question=answer.question, accepted=True).update(
            accepted=False
        )
        answer.accepted = True
        answer.save()

    return JsonResponse({"accepted": answer.accepted})


def centrifugo_token(request):
    payload = {
        "sub": str(request.user.id) if request.user.is_authenticated else "anonymous",
        "exp": int(time.time()) + 3600,
    }

    token = jwt.encode(payload, settings.CENTRIFUGO_TOKEN_SECRET, algorithm="HS256")

    return JsonResponse({"token": token})


def search_suggestions(request):
    query = request.GET.get("q", "").strip()

    if len(query) < 2:
        return JsonResponse({"results": []})

    # Полнотекстовый поиск
    search_vector = SearchVector("title", "text", config="russian") + SearchVector(
        "title", "text", config="english"
    )
    search_query = SearchQuery(query, config="russian") | SearchQuery(
        query, config="english"
    )

    questions = list(
        Question.objects.annotate(
            rank=SearchRank(search_vector, search_query),
        )
        .filter(rank__gt=0)
        .order_by("-rank")[:5]
    )

    # Если полнотекстовый поиск ничего не нашёл — ищем по вхождению
    if not questions:
        questions = list(
            Question.objects.filter(
                Q(title__icontains=query) | Q(text__icontains=query)
            )[:5]
        )

    results = [
        {
            "id": q.id,
            "title": q.title,
            "url": f"/question/{q.id}/",
        }
        for q in questions
    ]

    return JsonResponse({"results": results})
