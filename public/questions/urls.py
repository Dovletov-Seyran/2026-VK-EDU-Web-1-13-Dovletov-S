from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("ask/", views.AskView.as_view(), name="ask"),
    path("question/<int:question_id>/", views.QuestionView.as_view(), name="question"),
    path("tag/<str:tag_name>/", views.TagView.as_view(), name="tag"),
    path("hot/", views.HotView.as_view(), name="hot"),
    path("user/<str:username>/", views.UserView.as_view(), name="user"),
    path("question/vote/", views.question_vote, name="question_vote"),
    path("answer/vote/", views.answer_vote, name="answer_vote"),
    path("answer/accept/", views.accept_answer, name="accept_answer"),
]
