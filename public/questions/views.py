from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from .models import Question, Tag


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
            self.tag.questions.order_by("-created_at")
            .prefetch_related("tags")
            .select_related("user")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["tag"] = self.tag
        return context


class QuestionView(DetailView):
    template_name = "questions/question.html"
    context_object_name = "question"

    def get_object(self):
        return get_object_or_404(
            Question.objects.prefetch_related("tags").select_related("user"),
            id=self.kwargs["question_id"],
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        answers = self.object.answers.select_related("user").order_by("-created_at")
        from .utils import paginate

        page = paginate(answers, self.request)
        context["page_answer"] = page.object_list
        context["page"] = page
        return context


class AskView(ListView):
    template_name = "questions/ask.html"

    def get_queryset(self):
        return Question.objects.none()
