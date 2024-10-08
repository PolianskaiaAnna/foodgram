import csv

from django.conf import settings
from django.core.management.base import BaseCommand
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv-файла в базу данных.'

    def handle(self, *args, **kwargs):
        csv_file_path = settings.CSV_FILES_DIR / 'ingredients.csv'
        model = Ingredient
        self.stdout.write(f'Начинаем импорт из файла {csv_file_path}')
        with csv_file_path.open(mode='r', encoding='utf8') as f:
            reader = csv.reader(f)
            objects_to_create = [
                model(name=row[0], measurement_unit=row[1])
                for row in reader
            ]
            model.objects.bulk_create(
                objects_to_create,
                ignore_conflicts=True
            )
        self.stdout.write(self.style.SUCCESS(
            'Все данные загружены в базу')
        )
