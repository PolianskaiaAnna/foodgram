from django.core.exceptions import ValidationError


def validation_cooking_time(value):
    """Проверка времени приготовления"""
    if not value < 1:
        raise ValidationError('Время должно быть больше 1 минуты!')