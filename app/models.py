from math import ceil
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


# --------------------------- Tag ---------------------------
class Tag(models.Model):
    name = models.CharField(max_length=64, unique=True)

    def __str__(self):
        return self.name


# ---------------------- Question manager -------------------
class QuestionQuerySet(models.QuerySet):
    def _related(self):
        return (
            self.select_related("author", "author__profile")
                .prefetch_related("tags", "likes", "answers")
        )

    def feed_new(self):               # новые
        return self._related().order_by("-created_at")

    def feed_hot(self):               # популярные
        return (
            self._related()
                .annotate(likes_cnt=models.Count("likes"))
                .order_by("-likes_cnt", "-created_at")
        )

    def feed_by_tag(self, tag_name):
        return self._related().filter(tags__name=tag_name).order_by("-created_at")

    def full(self):
        return (
            self.select_related("author", "author__profile")
                .prefetch_related(
                    "tags",
                    "likes",
                    "answers",
                    "answers__likes",
                    "answers__author",
                    "answers__author__profile",
                )
        )


class QuestionManager(models.Manager):
    def get_queryset(self):
        return QuestionQuerySet(self.model, using=self._db)

    def feed_new(self):
        return self.get_queryset().feed_new()

    def feed_hot(self):
        return self.get_queryset().feed_hot()

    def feed_by_tag(self, tag_name):
        return self.get_queryset().feed_by_tag(tag_name)

    def full(self):
        return self.get_queryset().full()


# --------------------------- Question -----------------------
class Question(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    text = models.TextField()
    tags = models.ManyToManyField(Tag, related_name="questions")
    created_at = models.DateTimeField(auto_now_add=True)

    objects = QuestionManager()

    def get_absolute_url(self):
        return reverse("question_detail", args=[self.pk])

    def get_answers_queryset(self):
        return (
            self.answers
                .select_related("author", "author__profile")
                .prefetch_related("likes")
                .order_by("created_at")
        )

    def add_answer(self, *, author: User, form):
        answer = form.save(commit=False)
        answer.author = author
        answer.question = self
        answer.save()
        return answer

    def url_to_answer(self, answer, request, per_page=5):
        pos = self.get_answers_queryset().filter(pk__lte=answer.pk).count()
        page = ceil(pos / per_page)
        return f"{self.get_absolute_url()}?page={page}#answer{answer.pk}"

    @property
    def likes_count(self):
        return self.likes.count()

    @property
    def answers_count(self):
        return self.answers.count()

    def __str__(self):
        return self.title


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="answers")
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    is_correct = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Answer #{self.pk}"


class QuestionLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "question")


class AnswerLike(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="likes")

    class Meta:
        unique_together = ("user", "answer")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)

    def __str__(self):
        return f"Profile of {self.user.username}"
