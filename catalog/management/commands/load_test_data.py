from django.core.management.base import BaseCommand
from django.core.management import call_command
from catalog.models import Category, Product


class Command(BaseCommand):
    help = 'Удаляет все данные и загружает тестовые из фикстур'

    def handle(self, *args, **options):
        self.stdout.write('Удаляем старые данные...')
        Product.objects.all().delete()
        Category.objects.all().delete()

        self.stdout.write('Загружаем категории...')
        call_command('loaddata', 'categories.json')

        self.stdout.write('Загружаем продукты...')
        call_command('loaddata', 'products.json')

        self.stdout.write(self.style.SUCCESS('Готово! Тестовые данные загружены.'))