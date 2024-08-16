from django.db import models
from recipes.validators import validation_cooking_time
from users.models import User

LENG_NAME = 200
LENG_UNIT = 100


class Ingredient(models.Model):
    """Модель ингредиентов"""
    name = models.CharField(
        max_length=LENG_NAME,
        verbose_name='Название', unique=True
    )
    measurement_unit = models.CharField(
        verbose_name='Единица измерения',
        max_length=LENG_UNIT
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    """Модель тега"""
    name = models.CharField(verbose_name='Название', max_length=100)
    slug = models.SlugField(verbose_name='Слаг')

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецепта"""
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientRecipe',
        verbose_name='Ингредиент',
        related_name='recipes'
    )
    tags = models.ManyToManyField(
        Tag, verbose_name='Тег',
        through='TagRecipe',
        related_name='recipes',
    )
    image = models.ImageField(
        upload_to='static/images/',
        null=True,
        default=None,
        verbose_name='Изображение'
    )
    name = models.CharField(max_length=256, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveIntegerField(
        verbose_name='Время приготовления',
        validators=(validation_cooking_time,)
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
    )
    short_link = models.CharField(
        max_length=22, unique=True, null=True
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('name',)

    def __str__(self):
        return self.name

    def favorited_count(self):
        """Показывает сколько раз рецепт был добавлен в избранное."""
        return self.favorited_by.count()


class TagRecipe(models.Model):
    """Модель связи между рецептом и тэгом"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.recipe} {self.tag}'


class IngredientRecipe(models.Model):
    """Модель связи между рецептом и тэгом"""
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(verbose_name='Количество')

    def __str__(self):
        return f'{self.recipe} {self.ingredient}'


class Favorite(models.Model):
    """Модель для добавления рецептов в избранное"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'

    def __str__(self):
        return {self.user.username} - {self.recipe.name}


class ShoppingCart(models.Model):
    """Модель для добавление рецептов в список покупок"""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='shopping_lists',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        'Recipe', on_delete=models.CASCADE,
        related_name='in_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        unique_together = ('user', 'recipe')
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'

    def __str__(self):
        return f'{self.user.username} {self.recipe.name}'
