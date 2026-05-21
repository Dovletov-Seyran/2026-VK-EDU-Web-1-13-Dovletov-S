from django import forms
from django.utils.text import slugify

import uuid

from .models import Question, Answer, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        required=False,
        max_length=255,
        widget=forms.TextInput(
            attrs={
                "class": "field",
                "placeholder": "moon, park, puzzle",
            }
        ),
        help_text="Enter up to 3 tags separated by commas.",
        label="Tags",
    )

    class Meta:
        model = Question
        fields = ("title", "text")
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "field",
                    "placeholder": "How to build a moon park?",
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "field",
                    "placeholder": "Describe your question...",
                }
            ),
        }

    def clean_tags(self):
        tags_str = self.cleaned_data.get("tags", "")
        if not tags_str.strip():
            return []
        tag_names = [t.strip() for t in tags_str.split(",") if t.strip()]
        if len(tag_names) > 3:
            raise forms.ValidationError("Можно указать не более 3 тегов.")
        return tag_names

    def save(self, user, commit=True):
        question = super().save(commit=False)
        question.user = user
        question.slug = (
            slugify(question.title, allow_unicode=True)[:200]
            + "-"
            + uuid.uuid4().hex[:8]
        )
        if commit:
            question.save()
            for name in self.cleaned_data.get("tags", []):
                slug = slugify(name, allow_unicode=True) or name.lower().replace(
                    " ", "-"
                )
                tag, _ = Tag.objects.get_or_create(
                    slug=slug,
                    defaults={"title": name},
                )
                question.tags.add(tag)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(
                attrs={
                    "class": "field mb-3",
                    "placeholder": "Enter your answer here..",
                }
            ),
        }

    def save(self, user, question, commit=True):
        answer = super().save(commit=False)
        answer.user = user
        answer.question = question
        if commit:
            answer.save()
        return answer
