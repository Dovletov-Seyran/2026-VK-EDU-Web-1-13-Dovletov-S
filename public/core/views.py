from django.shortcuts import render

def profile(request):
    return render(request, "core/profile.html")

def login(request):
    return render(request, "core/login.html")

def signup(request):
    return render(request, "core/signup.html")
