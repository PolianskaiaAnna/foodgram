# Generated by Django 4.2.14 on 2024-08-06 04:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_ingredient_measurement_unit'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='cats/images/', verbose_name='Изображение'),
        ),
    ]
