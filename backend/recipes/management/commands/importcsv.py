import csv
from pathlib import Path

from django.core.management.base import BaseCommand
from django.conf import settings

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импорт данных из csv-файла в базу данных.'

    def handle(self, *args, **kwargs):
        csv_file_path = settings.CSV_FILES_DIR / 'ingredients.csv'
        model = Ingredient
        self.stdout.write(f'Начинаем импорт из файла {csv_file_path}')
        with csv_file_path.open(mode='r', encoding='utf8') as f:
            reader = csv.reader(f)
            counter = 0
            objects_to_create = []
            for row in reader:
                counter += 1
                name, measurement_unit = row
                objects_to_create.append(model(name=name, measurement_unit=measurement_unit))
            model.objects.bulk_create(
                objects_to_create,
                ignore_conflicts=True
            )
            # self.stdout.write(
            #     f'Данные из файла {file} импортированы')

        self.stdout.write(self.style.SUCCESS(
            'Все данные загружены в базу')
        )