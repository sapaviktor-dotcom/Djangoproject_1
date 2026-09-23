from django.urls import path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('', views.home, name='home'),  # главная страница
    path('contacts/', views.contacts, name='contacts'),  # страница контактов
]