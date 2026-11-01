from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import CustomUserCreationForm

# --- Регистрация ---
def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()

            # Отправка приветственного письма
            send_mail(
                'Добро пожаловать!',
                f'Привет, {user.username}! Спасибо за регистрацию.',
                settings.DEFAULT_FROM_EMAIL,  # Теперь Django знает, откуда брать email
                [user.email],
                fail_silently=False,
            )

            messages.success(request, 'Регистрация прошла успешно. Теперь вы можете войти.')
            return redirect('login')
    else:
            form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})


# --- Авторизация ---
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            return redirect('catalog:home')
        else:
            messages.error(request, 'Неверный email или пароль')

    return render(request, 'users/login.html')