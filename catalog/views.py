from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from django.core.paginator import Paginator

from .models import Product
from .forms import ProductForm


def home(request):
    """Главная: список товаров с пагинацией."""
    products = Product.objects.all()
    paginator = Paginator(products, 4)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'catalog/home.html', {'page_obj': page_obj})


def product_detail(request, pk):
    """Детальная страница товара."""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'catalog/product_detail.html', {'product': product})


def product_create(request):
    """Добавление нового товара."""
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save()
            messages.success(request, f'Товар «{product.name}» добавлен.')
            return redirect('catalog:home')
    else:
        form = ProductForm()
    return render(request, 'catalog/product_form.html', {'form': form})


@csrf_protect
def contacts(request):
    """Контакты + форма обратной связи."""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        if not (name and phone and message):
            messages.error(request, 'Заполните все поля формы.')
        else:
            print(f"Новое сообщение от {name} ({phone}): {message}")
            messages.success(request, f'Спасибо, {name}! Ваше сообщение отправлено.')

    context = {
        'country': 'USA',
        'inn': '91-1144442',
        'address': 'Redmond, WA, 98052-6399',
    }
    return render(request, 'catalog/contacts.html', context)