import os

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator

from .models import Product


#  список запрещённых слов в константе
FORBIDDEN_WORDS = (
    'казино',
    'криптовалюта',
    'крипта',
    'биржа',
    'дешево',
    'бесплатно',
    'обман',
    'полиция',
    'радар',
)

MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 МБ


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Задание 3: стилизация всех полей через __init__
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                css_class = 'form-check-input'
            elif isinstance(field.widget, forms.Select):
                css_class = 'form-select'
            else:
                css_class = 'form-control'
            field.widget.attrs.update({'class': css_class})

        #  валидатор расширения для изображения
        self.fields['image'].validators.append(
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png'])
        )
        self.fields['image'].widget.attrs.update({'accept': 'image/jpeg,image/png'})

    # ----------  запрещённые слова ----------
    @staticmethod
    def _check_forbidden_words(value):
        """Проверяет текст на наличие запрещённых слов (без учёта регистра)."""
        if not value:
            return value
        lowered = value.lower()
        for word in FORBIDDEN_WORDS:
            if word in lowered:
                raise ValidationError(
                    f'Слово «{word}» запрещено использовать в названии и описании продукта.'
                )
        return value

    def clean_name(self):
        return self._check_forbidden_words(self.cleaned_data.get('name', ''))

    def clean_description(self):
        return self._check_forbidden_words(self.cleaned_data.get('description', ''))

    # ----------  цена ----------
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is None:
            raise ValidationError('Укажите цену продукта.')
        if price < 0:
            raise ValidationError(
                f'Цена не может быть отрицательной. Вы указали: {price}. '
                f'Введите неотрицательное значение.'
            )
        return price

    # ----------  изображение ----------
    def clean_image(self):
        image = self.cleaned_data.get('image')
        if not image:
            return image

        # При редактировании без замены файла — объект уже сохранён, пропускаем
        if hasattr(image, 'content_type'):
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ('.jpg', '.jpeg', '.png'):
                raise ValidationError('Допустимы только файлы форматов JPEG или PNG.')
            if image.size > MAX_IMAGE_SIZE:
                raise ValidationError(
                    f'Размер изображения не должен превышать 5 МБ. '
                    f'Ваш файл весит {image.size / (1024 * 1024):.2f} МБ.'
                )
        return image