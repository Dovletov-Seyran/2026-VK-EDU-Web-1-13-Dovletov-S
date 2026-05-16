from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from .models import Profile


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(
            attrs={
                "class": "field",
                "placeholder": "Enter your login here",
            }
        ),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "field",
                "placeholder": "Enter your password",
            }
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")

        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Неверный логин или пароль.")
            cleaned_data["user"] = user

        return cleaned_data


class SignupForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "field",
                "placeholder": "Enter password",
            }
        ),
        label="Password",
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(
            attrs={
                "class": "field",
                "placeholder": "Repeat password",
            }
        ),
        label="Repeat password",
    )
    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "accept": "image/*",
                "id": "avatar-input",
                "style": "display:none",
            }
        ),
        label="Upload avatar",
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(
                attrs={
                    "class": "field",
                    "placeholder": "Enter your login",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "field",
                    "placeholder": "Enter your email",
                }
            ),
        }

    def clean_password(self):
        password = self.cleaned_data.get("password")
        if password:
            validate_password(password)
        return password

    def clean_password2(self):
        password = self.cleaned_data.get("password")
        password2 = self.cleaned_data.get("password2")

        if password and password2 and password != password2:
            raise ValidationError("Пароли не совпадают.")

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if email and User.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже зарегистрирован.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                avatar=self.cleaned_data.get("avatar"),
            )
        return user


class ProfileForm(forms.ModelForm):
    avatar = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(
            attrs={
                "accept": "image/*",
                "id": "avatar-input",
                "style": "display:none",
            }
        ),
        label="Upload avatar",
    )

    class Meta:
        model = User
        fields = ("username", "email")
        widgets = {
            "username": forms.TextInput(attrs={"class": "field"}),
            "email": forms.EmailInput(attrs={"class": "field"}),
        }

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if (
            email
            and User.objects.filter(email=email).exclude(pk=self.instance.pk).exists()
        ):
            raise ValidationError("Этот email уже используется другим пользователем.")
        return email

    def save(self, commit=True):
        user = super().save(commit=commit)
        if commit:
            profile, created = Profile.objects.get_or_create(user=user)
            avatar = self.cleaned_data.get("avatar")
            if avatar:
                profile.avatar = avatar
                profile.save()
        return user
