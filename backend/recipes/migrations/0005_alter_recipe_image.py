# Generated by Django 4.2.14 on 2024-08-07 07:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0004_alter_recipe_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='image',
            field=models.ImageField(default=None, null=True, upload_to='recipe/images/', verbose_name='Изображение'),
        ),
    ]
