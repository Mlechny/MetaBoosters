from django.http import Http404
from django.views.decorators.http import require_http_methods, require_safe
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Question, Tag
from .forms import LoginForm, SignupForm, AskForm, AnswerForm, ProfileEditForm
from .utils import paginate

SAFE_REDIRECT = "index"

@require_safe
def index(request):
    page = paginate(Question.objects.feed_new(), request, 5)
    return render(request, "index.html", {"page_obj": page})

@require_safe
def hot(request):
    page = paginate(Question.objects.feed_hot(), request, 5)
    return render(request, "hot.html", {"page_obj": page})

@require_safe
def tag(request, tag_name):
    if not Tag.objects.filter(name=tag_name).exists():
        raise Http404
    page = paginate(Question.objects.feed_by_tag(tag_name), request, 5)
    return render(request, "tag.html", {"page_obj": page, "tag_name": tag_name})

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect(SAFE_REDIRECT)

    form = LoginForm(request.POST or None)
    if form.is_valid():
        login(request, form.cleaned_data["user"])
        cont = request.GET.get("continue", reverse(SAFE_REDIRECT))
        if not url_has_allowed_host_and_scheme(cont, {request.get_host()}):
            cont = reverse(SAFE_REDIRECT)
        return redirect(cont)

    return render(request, "login.html", {"form": form})


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect(SAFE_REDIRECT)

    form = SignupForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        user = form.save()
        login(request, user)
        return redirect(SAFE_REDIRECT)

    return render(request, "signup.html", {"form": form})

@require_safe
def logout_view(request):
    logout(request)
    nxt = request.GET.get("next")
    if not url_has_allowed_host_and_scheme(nxt or "", {request.get_host()}):
        nxt = request.META.get("HTTP_REFERER", reverse(SAFE_REDIRECT))
    return redirect(nxt)

@login_required(login_url="/login/")
@require_http_methods(["GET", "POST"])
def ask_view(request):
    form = AskForm(request.POST or None)
    if form.is_valid():
        question = form.save(author=request.user)
        return redirect(question.get_absolute_url())
    return render(request, "ask.html", {"form": form})

@require_http_methods(["GET", "POST"])
def question_detail(request, question_id):
    question = get_object_or_404(Question.objects.full(), pk=question_id)
    page = paginate(question.get_answers_queryset(), request, 5)

    form = AnswerForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        if not request.user.is_authenticated:
            return redirect(f"{reverse('login')}?continue={request.path}")
        answer = question.add_answer(author=request.user, form=form)
        return redirect(question.url_to_answer(answer, request))

    return render(
        request,
        "question.html",
        {"question": question, "page_obj": page, "answer_form": form},
    )

@login_required(login_url="/login/")
@require_http_methods(["GET", "POST"])
def profile_edit_view(request):
    form = ProfileEditForm(
        request.POST or None,
        request.FILES or None,
        instance=request.user.profile,
        user=request.user,
    )
    if form.is_valid():
        form.save()
        return redirect(request.path)
    return render(request, "profile_edit.html", {"form": form})
