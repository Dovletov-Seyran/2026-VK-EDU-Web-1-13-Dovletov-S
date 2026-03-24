from django.urls import path

from . import views

app_name = 'app'

urlpatterns = [
    path("home/", views.index, name="home"),
    path("ask/", views.ask, name="ask"),
    path("profile/", views.profile, name="profile"),
    path("question/", views.question, name="question"),
    path("tag/", views.tag, name="tag"),
]


