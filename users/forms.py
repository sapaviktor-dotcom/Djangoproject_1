from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'avatar', 'phone', 'country')

    # Настраиваем виджет для аватара, чтобы он нормально работал с формой
    avatar = forms.ImageField(widget=forms.FileInput(attrs={'class': 'form-control'}), required=False)

    # Проверка, что такой email еще не занят
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Пользователь с таким email уже существует.")
        return email

    # Проверка, что такой username еще не занят
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Это имя пользователя уже занято.")
        return username

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "avatar", "phone", "country")