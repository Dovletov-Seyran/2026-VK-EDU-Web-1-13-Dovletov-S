from django.shortcuts import render



def index(request):
    return render(request, "app/index.html")

def ask(request):
    return render(request, "app/ask.html")

def profile(request):
    return render(request, "app/profile.html")

def question(request):
    return render(request, "app/question.html")

def tag(request):
    return render(request, "app/tag.html")
