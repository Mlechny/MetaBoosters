from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    page_number = request.GET.get('page', 1)  # считываем ?page= из URL
    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        page = paginator.page(1)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page

def index(request):
    questions = []
    for i in range(1, 31):
        questions.append({
            'id': i,
            'title': f'Вопрос {i}',
            'text': f'Текст вопроса {i}...'
        })

    page = paginate(questions, request, per_page=5)

    context = {
        'page_obj': page,
    }
    return render(request, 'index.html', context)

def hot(request):
    hot_questions = []
    for i in range(1, 31):
        hot_questions.append({
            'id': i,
            'title': f'Горячий вопрос {i}',
            'text': f'Текст горячего вопроса {i}'
        })

    page = paginate(hot_questions, request, per_page=5)

    context = {
        'page_obj': page,
    }
    return render(request, 'hot.html', context)

def tag(request, tag_name):
    tagged_questions = []
    for i in range(1, 21):
        tagged_questions.append({
            'id': i,
            'title': f'Вопрос с тегом {tag_name} #{i}',
            'text': f'...'
        })

    page = paginate(tagged_questions, request, per_page=5)

    context = {
        'page_obj': page,
        'tag_name': tag_name,
    }
    return render(request, 'tag.html', context)

def question_detail(request, question_id):
    question = {
        'id': question_id,
        'title': f'Детали вопроса {question_id}',
        'text': 'Полное описание здесь',
        'tags': ['Схема', 'Состав', 'События'],
        'answers': [
            {'id': 1, 'text': 'Ответ 1', 'is_correct': True},
            {'id': 2, 'text': 'Ответ 2', 'is_correct': False},
        ],
    }
    return render(request, 'question.html', {'question': question})

def login_view(request):
    return render(request, 'login.html')

def signup_view(request):
    return render(request, 'signup.html')

def ask_view(request):
    return render(request, 'ask.html')
