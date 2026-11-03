from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView  # Импортируем встроенный класс

urlpatterns = [
    # Страница регистрации
    path('register/', views.register_view, name='register'),

    # Страница входа
    path('login/', views.login_view, name='login'),

    # Маршрут для выхода (логаут) - используем встроенный класс Django
    path('logout/', LogoutView.as_view(next_page='catalog:home'), name='logout'),

    path("profile/", views.profile_view, name="profile"),
]

