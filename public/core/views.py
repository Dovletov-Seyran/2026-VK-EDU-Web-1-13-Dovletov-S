from django.shortcuts import redirect
from django.views import View
from django.views.generic import FormView
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.http import url_has_allowed_host_and_scheme

from .forms import LoginForm, SignupForm, ProfileForm


class LoginView(FormView):
    template_name = "core/login.html"
    form_class = LoginForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            next_url = self.get_next_url()
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}
            ):
                return redirect(next_url)
            return redirect("questions:home")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["next"] = self.get_next_url()
        return context

    def get_next_url(self):
        return self.request.GET.get("next", self.request.POST.get("next", ""))

    def form_valid(self, form):
        user = form.cleaned_data["user"]
        auth_login(self.request, user)
        next_url = self.get_next_url()
        if next_url and url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={self.request.get_host()}
        ):
            return redirect(next_url)
        return redirect("questions:home")


class SignupView(FormView):
    template_name = "core/signup.html"
    form_class = SignupForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        if self.request.method == "POST":
            kwargs["files"] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        user = form.save()
        auth_login(self.request, user)
        return redirect("questions:home")


class LogoutView(View):
    def get(self, request):
        referer = request.META.get("HTTP_REFERER", "/")
        auth_logout(request)
        if url_has_allowed_host_and_scheme(referer, allowed_hosts={request.get_host()}):
            return redirect(referer)
        return redirect("questions:home")


class ProfileView(LoginRequiredMixin, FormView):
    template_name = "core/profile.html"
    form_class = ProfileForm
    login_url = "/login/"

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["instance"] = self.request.user
        if self.request.method == "POST":
            kwargs["files"] = self.request.FILES
        return kwargs

    def form_valid(self, form):
        form.save()
        return redirect("core:profile")
