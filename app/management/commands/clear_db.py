from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike

class Command(BaseCommand):
    help = "Очищает все тестовые данные, кроме суперпользователя"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Удаление лайков..."))
        QuestionLike.objects.all().delete()
        AnswerLike.objects.all().delete()

        self.stdout.write(self.style.WARNING("Удаление ответов и вопросов..."))
        Answer.objects.all().delete()
        Question.objects.all().delete()

        self.stdout.write(self.style.WARNING("Удаление тегов..."))
        Tag.objects.all().delete()

        self.stdout.write(self.style.WARNING("Удаление профилей и пользователей..."))
        Profile.objects.all().delete()
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("База очищена. Суперпользователь сохранён."))
