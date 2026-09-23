from django.shortcuts import render
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect


def home(request):
    """Контроллер для главной страницы"""
    context = {
        'products': [
            {
                'name': 'Удобный сервис рассылок',
                'price': '140',
                'description': 'Неограниченная лицензия, поддержка, установка на сервер, получение обновлений',
                'features': [
                    'Неограниченная лицензия',
                    'Поддержка',
                    'Установка на сервер',
                    'Получение обновлений'
                ]
            },
            {
                'name': 'Телеграм бот для бизнеса',
                'price': '200',
                'description': 'Автоматизация продаж, уведомления, интеграция с CRM',
                'features': [
                    'Автоматизация продаж',
                    'Уведомления',
                    'Интеграция с CRM',
                    'Аналитика'
                ]
            },
            {
                'name': 'Веб-приложение для управления задачами',
                'price': '300',
                'description': 'Управление проектами, задачи, сроки, отчеты',
                'features': [
                    'Управление проектами',
                    'Задачи и сроки',
                    'Отчеты',
                    'Командная работа'
                ]
            },
            {
                'name': 'Микросервис для обработки платежей',
                'price': '250',
                'description': 'Безопасные платежи, интеграция с платежными системами',
                'features': [
                    'Безопасные платежи',
                    'Интеграция с платежными системами',
                    'Автоматические уведомления',
                    'История транзакций'
                ]
            }
        ]
    }
    return render(request, 'catalog/home.html', context)


@csrf_protect
def contacts(request):
    """Контроллер для страницы контактов с формой обратной связи"""
    if request.method == 'POST':
        name = request.POST.get('name', '')
        phone = request.POST.get('phone', '')
        message = request.POST.get('message', '')

        # В реальном проекте здесь была бы отправка email или сохранение в БД
        print(f"Новое сообщение от {name} (Телефон: {phone}): {message}")

        # Добавляем сообщение об успешной отправке
        messages.success(request, f'Спасибо, {name}! Ваше сообщение успешно отправлено.')

        # Очищаем форму - возвращаем пустую страницу с сообщением

    context = {
        'country': 'USA',
        'inn': '91-1144442',
        'address': 'Redmond, WA, 98052-6399',
    }
    return render(request, 'catalog/contacts.html', context)