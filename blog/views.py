from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import BlogPost


class BlogPostListView(ListView):
    model = BlogPost
    template_name = 'blog/blogpost_list.html'
    context_object_name = 'posts'

    def get_queryset(self):
        # Только опубликованные
        return BlogPost.objects.filter(is_published=True)


class BlogPostDetailView(DetailView):
    model = BlogPost
    template_name = 'blog/blogpost_detail.html'
    context_object_name = 'post'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Увеличение счётчика просмотров
        obj.views_count += 1
        obj.save(update_fields=['views_count'])
        # Доп. задание: поздравление при достижении 100 просмотров
        if obj.views_count == 100:
            from django.core.mail import send_mail
            send_mail(
                subject='Поздравляем!',
                message=f'Статья «{obj.title}» набрала 100 просмотров!',
                from_email=None,
                recipient_list=['your_email@example.com'],
            )
        return obj


class BlogPostCreateView(CreateView):
    model = BlogPost
    fields = ['title', 'content', 'preview', 'is_published']
    template_name = 'blog/blogpost_form.html'
    success_url = reverse_lazy('blog:blogpost_list')


class BlogPostUpdateView(UpdateView):
    model = BlogPost
    fields = ['title', 'content', 'preview', 'is_published']
    template_name = 'blog/blogpost_form.html'

    def get_success_url(self):
        # Перенаправление на статью после редактирования
        return reverse_lazy('blog:blogpost_detail', kwargs={'pk': self.object.pk})


class BlogPostDeleteView(DeleteView):
    model = BlogPost
    template_name = 'blog/blogpost_confirm_delete.html'
    success_url = reverse_lazy('blog:blogpost_list')