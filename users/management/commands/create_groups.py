from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from catalog.models import Product  # Импортируем вашу модель товара
from blog.models import BlogPost

class Command(BaseCommand):
    help = 'Создает группы и назначает им права доступа'

    def handle(self, *args, **kwargs):
        # --- 1. Группа "Модератор продуктов" ---
        moderator_group, created = Group.objects.get_or_create(name='Модератор продуктов')

        # Получаем ContentType для модели Product
        product_content_type = ContentType.objects.get_for_model(Product)

        # Получаем нужные права
        # 1. Кастомное право (которое мы добавили в Meta)
        permission_unpublish = Permission.objects.get(
            codename='can_unpublish_product',
            content_type=product_content_type,
        )
        # 2. Стандартное право на удаление
        permission_delete = Permission.objects.get(
            codename='delete_product',
            content_type=product_content_type,
        )

        # Назначаем права группе
        moderator_group.permissions.add(permission_unpublish, permission_delete)

        if created:
            self.stdout.write(self.style.SUCCESS('Группа "Модератор продуктов" создана.'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Модератор продуктов" уже существует. Права обновлены.'))

        # --- 2. Группа "Контент-менеджер" (Доп. задание) ---
        # Раскомментируйте этот блок, если выполняете задание со звездочкой
        
        content_manager_group, created_cm = Group.objects.get_or_create(name='Контент-менеджер')

        blog_content_type = ContentType.objects.get_for_model(BlogPost)

        # Права на изменение и удаление постов блога
        permission_change_blog = Permission.objects.get(
            codename='change_blogpost',
            content_type=blog_content_type,
        )
        permission_delete_blog = Permission.objects.get(
            codename='delete_blogpost',
            content_type=blog_content_type,
        )

        content_manager_group.permissions.add(permission_change_blog, permission_delete_blog)

        if created_cm:
            self.stdout.write(self.style.SUCCESS('Группа "Контент-менеджер" создана.'))
        else:
            self.stdout.write(self.style.WARNING('Группа "Контент-менеджер" уже существует.'))


        self.stdout.write(self.style.SUCCESS('Все команды успешно выполнены!'))