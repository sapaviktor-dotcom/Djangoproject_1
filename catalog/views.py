from django.urls import reverse_lazy
from django.shortcuts import redirect, get_object_or_404  
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView
from django.views import View  # <-- Добавили View
from django.http import HttpResponseForbidden
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from .models import Product
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


class ProductCreateView(LoginRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
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

class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'  # используем тот же шаблон, что и для создания

    def get_success_url(self):
        # Возвращаем пользователя на страницу отредактированного товара
        messages.success(self.request, f'Товар «{self.object.name}» успешно обновлён.')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})

    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        # Владелец или модератор
        if request.user == product.owner or request.user.has_perm('catalog.can_unpublish_product'):
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("У вас нет прав на изменение этого продукта.")



class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        # Сохраняем название до удаления, чтобы вывести его в сообщении
        product_name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Товар «{product_name}» удалён.')
        return response

    def dispatch(self, request, *args, **kwargs):
        product = self.get_object()
        # Разрешаем, если владелец или модератор
        if request.user == product.owner or request.user.has_perm('catalog.can_unpublish_product'):
            return super().dispatch(request, *args, **kwargs)
        return HttpResponseForbidden("У вас нет прав на удаление этого продукта.")


class ProductUnpublishView(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'catalog.can_unpublish_product'
    raise_exception = True  # Выдаст 403, если прав нет

    def post(self, request, pk):
        product = get_object_or_404(Product, pk=pk)

        # Меняем статус на "Снят с публикации"
        product.status = 'unpublished'
        product.save()

        messages.success(request, f'Товар «{product.name}» снят с публикации.')
        return redirect('catalog:product_detail', pk=product.pk)