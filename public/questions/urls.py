from django.urls import path
from . import views

app_name = "questions"

urlpatterns = [
    path("", views.IndexView.as_view(), name="home"),
    path("ask/", views.AskView.as_view(), name="ask"),
    path("question/<int:question_id>/", views.QuestionView.as_view(), name="question"),
    path("tag/<str:tag_name>/", views.TagView.as_view(), name="tag"),
    path("hot/", views.HotView.as_view(), name="hot"),
]
