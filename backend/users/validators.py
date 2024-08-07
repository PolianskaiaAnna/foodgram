from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError

username_validator = RegexValidator(
    regex=r'^[\w.@+-]+\Z',
    message='Юзернейм содержит недопустимые символы',
    code='invalid_username'
)


def username_not_me(value):
    if value.lower() == 'me':
        raise ValidationError('Нельзя использовать имя me')