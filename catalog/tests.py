from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Product, Category

User = get_user_model()


class ProductAccessTest(TestCase):
    def setUp(self):
        # Создаём тестовую категорию
        self.category = Category.objects.create(name='Тестовая категория')
        # Создаём трёх пользователей: владелец, модератор, посторонний
        self.owner = User.objects.create_user(email='owner@test.ru', username='owner', password='test12345')
        self.moderator = User.objects.create_user(email='mod@test.ru', username='mod', password='test12345')
        self.stranger = User.objects.create_user(email='stranger@test.ru', username='stranger', password='test12345')

        # Назначаем модератора в группу
        mod_group = Group.objects.create(name='Модератор продуктов')
        content_type = ContentType.objects.get_for_model(Product)

        # Добавляем право can_unpublish_product в группу
        try:
            perm_unpublish = Permission.objects.get(codename='can_unpublish_product', content_type=content_type)
            mod_group.permissions.add(perm_unpublish)
        except Permission.DoesNotExist:
            pass

        self.moderator.groups.add(mod_group)

        # Создаём товар от лица владельца
        self.product = Product.objects.create(
            name='Тестовый товар',
            category=self.category,
            price=100.00,
            owner=self.owner,
            status='published'
        )

    def test_owner_can_update_product(self):
        """Владелец может редактировать свой товар"""
        self.client.login(email='owner@test.ru', password='test12345')
        url = reverse('catalog:product_update', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_stranger_cannot_update_product(self):
        """Посторонний пользователь НЕ может редактировать чужой товар"""
        self.client.login(email='stranger@test.ru', password='test12345')
        url = reverse('catalog:product_update', kwargs={'pk': self.product.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_moderator_can_delete_product(self):
        """Модератор может удалить любой товар"""
        self.client.login(email='mod@test.ru', password='test12345')
        url = reverse('catalog:product_delete', kwargs={'pk': self.product.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # Редирект после удаления
        self.assertFalse(Product.objects.filter(pk=self.product.pk).exists())

    def test_owner_can_unpublish_product(self):
        """Модератор может снять товар с публикации"""
        self.client.login(email='mod@test.ru', password='test12345')
        url = reverse('catalog:product_unpublish', kwargs={'pk': self.product.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)

        self.product.refresh_from_db()
        self.assertEqual(self.product.status, 'unpublished')

    def test_stranger_cannot_unpublish_product(self):
        """Посторонний не может снять товар с публикации"""
        self.client.login(email='stranger@test.ru', password='test12345')
        url = reverse('catalog:product_unpublish', kwargs={'pk': self.product.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 403)

    def test_anonymous_cannot_access_protected_views(self):
        """Анонимный пользователь не может зайти на защищённые страницы"""
        urls = [
            reverse('catalog:product_update', kwargs={'pk': self.product.pk}),
            reverse('catalog:product_delete', kwargs={'pk': self.product.pk}),
            reverse('catalog:product_unpublish', kwargs={'pk': self.product.pk}),
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertIn(response.status_code, [302, 403])  # Редирект на логин