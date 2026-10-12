from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, TemplateView, UpdateView, DeleteView

from .models import Product
from .forms import ProductForm


class ProductListView(ListView):
    model = Product
    template_name = 'catalog/home.html'
    context_object_name = 'page_obj'
    paginate_by = 4


class ProductDetailView(DetailView):
    model = Product
    template_name = 'catalog/product_detail.html'
    context_object_name = 'product'


class ProductCreateView(CreateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
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

class ProductUpdateView(UpdateView):
    model = Product
    form_class = ProductForm
    template_name = 'catalog/product_form.html'  # используем тот же шаблон, что и для создания

    def get_success_url(self):
        # Возвращаем пользователя на страницу отредактированного товара
        messages.success(self.request, f'Товар «{self.object.name}» успешно обновлён.')
        return reverse_lazy('catalog:product_detail', kwargs={'pk': self.object.pk})


class ProductDeleteView(DeleteView):
    model = Product
    template_name = 'catalog/product_confirm_delete.html'
    success_url = reverse_lazy('catalog:home')

    def form_valid(self, form):
        # Сохраняем название до удаления, чтобы вывести его в сообщении
        product_name = self.object.name
        response = super().form_valid(form)
        messages.success(self.request, f'Товар «{product_name}» удалён.')
        return response