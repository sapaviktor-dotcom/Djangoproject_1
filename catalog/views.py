from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.http import Http404

from .services import (
    get_products_by_category,
    invalidate_category_cache,
    get_product_by_id,
    invalidate_product_cache
)
from .models import Product, Category
from .forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'page_obj'
    paginate_by = 4


class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'

    # Убрали cache_page! Кешируем данные через сервисную функцию
    def get_object(self, queryset=None):
        product_id = self.kwargs.get('pk')
        product = get_product_by_id(product_id)
        if product is None:
            raise Http404("Товар не найден")
        return product


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        invalidate_category_cache(self.object.category_id)  # Сброс кеша категории
        messages.success(self.request, f'Товар «{self.object.name}» добавлен.')
        return response


class ContactsView(TemplateView):
    template_name = 'catalog/contacts.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'country': 'USA',
            'inn': '91-1144442',
            'address': 'Redmond, WA, 98052-6399',
        })
        return context

    def post(self, request, *args, **kwargs):
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        message = request.POST.get('message', '').strip()

        if not (name and phone and message):
            messages.error(request, 'Заполните все поля формы.')
        else:
            print(f"Новое сообщение от {name} ({phone}): {message}")
            messages.success(request, f'Спасибо, {name}! Ваше сообщение отправлено.')

        return redirect('catalog:contacts')


class ProductUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    raise_exception = True

    def test_func(self):
        product = self.get_object()
        return (
                self.request.user == product.owner or
                self.request.user.has_perm('catalog.can_unpublish_product')
        )

    def get_success_url(self):
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def form_valid(self, form):
        old_category_id = self.object.category_id  # Запоминаем до сохранения
        response = super().form_valid(form)
        new_category_id = self.object.category_id

        # Сбрасываем кеш товара и категории
        invalidate_product_cache(self.object.pk)
        invalidate_category_cache(old_category_id)
        if old_category_id != new_category_id:
            invalidate_category_cache(new_category_id)

        messages.success(self.request, f'Товар «{self.object.name}» успешно обновлён.')
        return response


class ProductDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')
    raise_exception = True

    def test_func(self):
        product = self.get_object()
        return (
                self.request.user == product.owner or
                self.request.user.has_perm('catalog.can_unpublish_product')
        )

    def form_valid(self, form):
        product_id = self.object.pk
        category_id = self.object.category_id
        product_name = self.object.name

        response = super().form_valid(form)

        # Сбрасываем кеш товара и категории
        invalidate_product_cache(product_id)
        invalidate_category_cache(category_id)

        messages.success(self.request, f'Товар «{product_name}» удалён.')
        return response


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'catalog.can_unpublish_product'
    raise_exception = True

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)
        product.status = 'unpublished'
        product.save()
        invalidate_product_cache(product.pk)  # Сброс кеша товара
        invalidate_category_cache(product.category_id)  # Сброс кеша категории
        messages.success(request, f'Товар «{product.name}» снят с публикации.')
        return redirect('catalog:product_detail', pk=product.pk)


def category_products_view(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = get_products_by_category(category_id)
    return render(request, 'catalog/category_products.html', {
        'category': category,
        'products': products,
    })