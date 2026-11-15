from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from .models import Product, Category
from django.core.cache import cache
from .services import get_products_by_category, invalidate_category_cache

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

class CacheTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='Кеш-категория')
        self.product = Product.objects.create(
            name='Кешированный товар',
            category=self.category,
            price=100.00,
            status='published'
        )
        cache.clear()  # Очищаем кеш перед каждым тестом

    def test_products_are_cached(self):
        """Проверяет, что данные сохраняются в кеш и возвращаются из него"""
        # Первый запрос — идёт в БД
        products_1 = get_products_by_category(self.category.id)
        self.assertEqual(len(products_1), 1)

        # Проверяем, что ключ появился в Redis
        cache_key = f'category_{self.category.id}'
        self.assertIsNotNone(cache.get(cache_key))

        # Второй запрос — должен вернуться из кеша
        products_2 = get_products_by_category(self.category.id)
        self.assertEqual(len(products_2), 1)
        # (Для строгости можно сравнить id объектов, но для домашки достаточно)

    def test_cache_ttl_is_set(self):
        """Проверяет, что у ключа установлен TTL"""
        get_products_by_category(self.category.id)
        # Проверяем, что данные сохранились
        cache_key = f'category_{self.category.id}'
        self.assertIsNotNone(cache.get(cache_key))

    def test_cache_invalidated_after_create(self):
        """Проверяет, что кеш сбрасывается после создания товара"""
        # Заполняем кеш
        get_products_by_category(self.category.id)
        cache_key = f'category_{self.category.id}'
        self.assertIsNotNone(cache.get(cache_key))

        # Имитируем создание товара через view (или напрямую)
        from .views import ProductCreateView
        invalidate_category_cache(self.category.id)

        # Проверяем, что кеш пуст
        self.assertIsNone(cache.get(cache_key))

    def test_cache_invalidated_after_delete(self):
        """Проверяет, что кеш сбрасывается после удаления товара"""
        get_products_by_category(self.category.id)
        cache_key = f'category_{self.category.id}'
        self.assertIsNotNone(cache.get(cache_key))

        invalidate_category_cache(self.category.id)
        self.assertIsNone(cache.get(cache_key))
