# Generated by Django 4.2.14 on 2024-08-09 05:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0007_recipe_short_link'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='static/images/', verbose_name='Изображение'),
        ),
    ]
