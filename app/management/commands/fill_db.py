# management/commands/fill_db.py
import os
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from MetaBoosters import settings
from app.models import Profile, Tag, Question, Answer, QuestionLike, AnswerLike
from itertools import product


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('ratio', type=int, help='Multiplier ratio for generated data')

    def handle(self, *args, **options):
        ratio: int = options["ratio"]

        # Тематические шаблоны FIFA
        question_titles = [
            "Как забить со штрафного в FIFA 24?",
            "Какая лучшая тактика для раша?",
            "Какой игрок самый быстрый в FIFA 23?",
            "Почему вратарь не двигается при пенальти?",
            "Лучшие связки игроков в составе из АПЛ?",
            "Стоит ли качать защитников на навесы?",
            "Как использовать фейковые движения?",
            "Кто лучший нападающий в FIFA 24?",
            "Сколько монет нужно для хорошего состава?",
            "Как лучше всего реализовывать угловые?",
            "Какие карточки самые метовые?",
            "Как повысить химию в составе?",
        ]

        question_texts = [
            "Уже неделю играю и не понимаю, как стабильно забивать штрафные. Подскажите!",
            "Нужен совет по схеме 4-2-3-1. Кто как играет?",
            "Слышал, что Мбаппе самый быстрый. Это так?",
            "Иногда вратарь просто замирает на месте. Баг или что-то не так делаю?",
            "Хочу собрать состав из игроков АПЛ. Кто сейчас в мета?",
            "Что лучше — длинные навесы или прострелы?",
            "Кто топовый ЦАП на бюджет до 100к?",
            "Какие навыки лучше качать для фланговых защитников?",
            "Как работает динамическая тактика в FIFA?",
            "Какие стили сыгранности самые эффективные?",
        ]

        tag_names = [
            "штрафные", "тактика", "игроки", "вратари", "АПЛ", "Ultimate Team",
            "финты", "навыки", "состав", "мета", "карточки", "химия", "угловые", "пенальти"
        ]

        answer_texts = [
            "Попробуй зажать R1 при ударе — тогда мяч пойдёт точно в угол.",
            "Схема 4-3-3 работает лучше, если играешь от флангов.",
            "Да, Мбаппе и Винисиус самые быстрые на сегодняшний день.",
            "Это баг в версии 1.04, после обновления должно исправиться.",
            "В АПЛ сейчас топовые — Холанд, Де Брюйне и Сака.",
            "Не забудь про тактику давления после потери мяча.",
            "Химия команды влияет на пас и скорость — стоит прокачивать.",
            "Лучше не использовать автозащиту — она часто даёт сбои.",
            "Для пенальти лучше нацеливаться чуть ниже перекладины.",
            "Подача с углового на ближнюю штангу — почти всегда гол!",
        ]

        default_avatar_path = os.path.join(
            settings.BASE_DIR, "static", "img", "some_logo.jpeg"
        )
        with open(default_avatar_path, "rb") as f:
            avatar_bytes = f.read()

        self.stdout.write(self.style.SUCCESS("Создание пользователей и профилей..."))
        users = []
        for i in range(ratio):
            username = f"fifa_user_{i}_{random.randint(1000, 9999)}"
            email = f"{username}@example.com"
            password = f"pass{i + 1}"
            user = User.objects.create_user(username=username, email=email, password=password)

            # создаём профиль + аватар
            profile = Profile.objects.create(user=user)
            avatar_content = ContentFile(avatar_bytes, name="avatar.jpeg")
            profile.avatar.save("avatar.jpeg", avatar_content, save=True)

            users.append(user)

        self.stdout.write(self.style.SUCCESS("Создание тегов..."))
        tags = []
        for idx, name in enumerate(tag_names, 1):
            tag_name = f"{name}.{idx}"
            tag, _ = Tag.objects.get_or_create(name=tag_name)
            tags.append(tag)

        self.stdout.write(self.style.SUCCESS("Создание вопросов..."))
        questions = []
        for _ in range(ratio * 10):
            author = random.choice(users)
            question = Question.objects.create(
                author=author,
                title=random.choice(question_titles),
                text=random.choice(question_texts),
            )
            question.tags.add(*random.sample(tags, k=random.randint(1, 3)))
            questions.append(question)

        self.stdout.write(self.style.SUCCESS("Создание ответов..."))
        answers = []
        for _ in range(ratio * 100):
            author = random.choice(users)
            question = random.choice(questions)
            answer = Answer.objects.create(
                author=author,
                question=question,
                text=random.choice(answer_texts),
                is_correct=random.choice([True, False]),
            )
            answers.append(answer)

        num_likes_needed = ratio * 200

        # Собираем все возможные пары user-вопрос и user-ответ (для уникальности)
        question_pairs = list(product(users, questions))
        answer_pairs = list(product(users, answers))
        all_pairs = [("question", user, obj) for user, obj in question_pairs] + \
                    [("answer", user, obj) for user, obj in answer_pairs]

        # Если лайков нужно больше, чем уникальных пар — ограничиваем максимумом
        max_likes = len(all_pairs)
        if num_likes_needed > max_likes:
            self.stdout.write(self.style.WARNING(
                f"Можно создать только {max_likes} уникальных лайков (у вас {num_likes_needed} требуется)."
            ))
            num_likes_needed = max_likes

        # Перемешиваем пары и берём первые N
        random.shuffle(all_pairs)
        selected_pairs = all_pairs[:num_likes_needed]

        count_q = 0
        count_a = 0
        for pair_type, user, obj in selected_pairs:
            if pair_type == "question":
                QuestionLike.objects.create(user=user, question=obj)
                count_q += 1
            else:
                AnswerLike.objects.create(user=user, answer=obj)
                count_a += 1

        self.stdout.write(self.style.SUCCESS("База данных успешно заполнена тематическими FIFA-данными."))
