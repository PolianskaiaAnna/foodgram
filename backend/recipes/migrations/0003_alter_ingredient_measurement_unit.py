# Generated by Django 4.2.14 on 2024-08-04 11:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_rename_test_recipe_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredient',
            name='measurement_unit',
            field=models.CharField(max_length=100, verbose_name='Единица измерения'),
        ),
    ]
