from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("hot/", views.hot, name="hot"),
    path("tag/<str:tag_name>/", views.tag, name="tag"),
    path("question/<int:question_id>/", views.question_detail, name="question_detail"),

    # формы авторизации/регистрации
    path("login/", views.login_view, name="login"),
    path("signup/", views.signup_view, name="signup"),
    path("logout/", views.logout_view, name="logout"),

    # добавление вопроса и редактирование профиля
    path("ask/", views.ask_view, name="ask"),
    path("profile/edit/", views.profile_edit_view, name="settings"),
]