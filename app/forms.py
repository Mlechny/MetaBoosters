from django import forms
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, password_validation
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _

from .models import Question, Answer, Tag, Profile

USERNAME_VALIDATOR = RegexValidator(r"^[A-Za-z0-9_]{3,30}$", _("Используйте 3‑30 символов: латиницу, цифры и подчёркивания"))
TAG_VALIDATOR = RegexValidator(r"^[\w.\-]{1,32}$", _("Тег может содержать буквы, цифры, '.', '_' и '-' (до 32 символов)"))
class LoginForm(forms.Form):
    username = forms.CharField(label="Логин", max_length=150)
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get("username")
        password = cleaned_data.get("password")
        if username and password:
            user = authenticate(username=username, password=password)
            if user is None:
                raise ValidationError("Неверный логин или пароль")
            cleaned_data["user"] = user
        return cleaned_data

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput)
    password2 = forms.CharField(label="Подтверждение пароля", widget=forms.PasswordInput)
    avatar = forms.ImageField(label="Аватар (необязательно)", required=False)

    class Meta:
        model = User
        fields = ("username", "email")
        labels = {"username": "Логин", "email": "E-mail"}
        help_texts = {"username": "Латиница, цифры и '_' (3-30 символов)"}

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        USERNAME_VALIDATOR(username)
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("Такой логин уже занят")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError("Пользователь с таким e-mail уже зарегистрирован")
        return email

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("password1")
        p2 = cleaned_data.get("password2")
        if p1 and p2:
            if p1 != p2:
                raise ValidationError("Пароли не совпадают")
            password_validation.validate_password(p1, user=None)
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["username"]
        user.email = self.cleaned_data["email"].lower()
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
            profile = Profile.objects.create(user=user)
            avatar = self.cleaned_data.get("avatar")
            if avatar:
                profile.avatar = avatar
                profile.save()
        return user

class AskForm(forms.ModelForm):
    tags = forms.CharField(label="Теги (через запятую)", help_text="До 5 тегов, каждый до 32 символов")

    class Meta:
        model = Question
        fields = ("title", "text")
        labels = {"title": "Заголовок", "text": "Текст вопроса"}
        help_texts = {"text": "Минимум 30 символов"}

    def clean_title(self):
        title = self.cleaned_data["title"].strip()
        if not (10 <= len(title) <= 150):
            raise ValidationError("Длина заголовка должна быть от 10 до 150 символов")
        return title

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if len(text) < 30:
            raise ValidationError("Текст вопроса слишком короткий (минимум 30 символов)")
        return text

    def clean_tags(self):
        raw = self.cleaned_data["tags"]
        tag_names = [t.strip() for t in raw.split(",") if t.strip()]
        if not tag_names:
            raise ValidationError("Добавьте хотя бы один тег")
        if len(tag_names) > 5:
            raise ValidationError("Максимум 5 тегов")
        unique_names = []
        for name in tag_names:
            TAG_VALIDATOR(name)
            if name.lower() in unique_names:
                raise ValidationError(f"Дубликат тега: {name}")
            unique_names.append(name.lower())
        return tag_names

    def save(self, author, commit=True):
        question = super().save(commit=False)
        question.author = author
        if commit:
            question.save()
            for name in self.cleaned_data["tags"]:
                tag, _ = Tag.objects.get_or_create(name=name)
                question.tags.add(tag)
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text",)
        labels = {"text": "Ваш ответ"}

    def clean_text(self):
        text = self.cleaned_data["text"].strip()
        if len(text) < 10:
            raise ValidationError("Ответ слишком короткий (минимум 10 символов)")
        return text

    def save(self, author, question, commit=True):
        answer = super().save(commit=False)
        answer.author = author
        answer.question = question
        if commit:
            answer.save()
        return answer

class ProfileEditForm(forms.ModelForm):
    username = forms.CharField(label="Логин", max_length=150, validators=[USERNAME_VALIDATOR])
    email = forms.EmailField(label="E‑mail")

    class Meta:
        model = Profile
        fields = ("avatar",)
        labels = {"avatar": "Аватар"}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        # начальные значения
        self.fields["username"].initial = self.user.username
        self.fields["email"].initial = self.user.email

    def clean_username(self):
        username = self.cleaned_data["username"].strip()
        USERNAME_VALIDATOR(username)
        if (User.objects.filter(username__iexact=username).exclude(pk=self.user.pk).exists()):
            raise ValidationError("Такой логин уже занят")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"].lower()
        if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError("Этот e‑mail уже используется")
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get("avatar")
        if avatar:
            if avatar.size > 2 * 1024 * 1024:
                raise ValidationError("Размер файла не должен превышать 2 МБ")
            if not avatar.content_type.startswith("image/"):
                raise ValidationError("Загрузите изображение")
        return avatar

    def save(self, commit=True):
        profile = super().save(commit=False)
        self.user.username = self.cleaned_data["username"]
        self.user.email = self.cleaned_data["email"]
        if commit:
            self.user.save()
            profile.user = self.user
            profile.save()
        return profile