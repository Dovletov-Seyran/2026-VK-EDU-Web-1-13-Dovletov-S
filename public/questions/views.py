from django.views.generic import ListView, DetailView, FormView, View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count

from .models import Question, Tag
from .forms import QuestionForm, AnswerForm
from .utils import paginate

from django.contrib.auth.models import User


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
            self.tag.questions.annotate(likes_count=Count("likes"))
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
            Question.objects.annotate(likes_count=Count("likes"))
            .prefetch_related("tags")
            .select_related("user"),
            id=question_id,
        )

    def get_context(self, question, form, request):
        answers = (
            question.answers.select_related("user")
            .annotate(likes_count=Count("likes"))
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
            answers = (
                question.answers.select_related("user")
                .annotate(likes_count=Count("likes"))
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
            .annotate(likes_count=Count("likes"))
            .order_by("-created_at")
            .prefetch_related("tags")
            .select_related("user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["profile_user"] = self.profile_user
        return context
