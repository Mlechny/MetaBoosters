from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),  # Главная
    path('hot/', views.hot, name='hot'),  # "Горячие" вопросы
    path('tag/<str:tag_name>/', views.tag, name='tag'),  # Вопросы по тегу
    path('question/<int:question_id>/', views.question_detail, name='question_detail'),
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('ask/', views.ask_view, name='ask'),
]
