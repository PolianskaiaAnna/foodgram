from django.contrib import admin

from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'image',
        'name',
        'text',
        'cooking_time',
        'author',
        'short_link',
        'favorited_count'
    )
    list_editable = (
        'name',
        'text',
        'cooking_time'
    )
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    filter_horizontal = ('ingredients', 'tags')


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit'
    )

    search_fields = ('name',)

    @admin.display(description='Добавлен в избранное (раз)')
    def favorited_count(self, obj):
        """Показывает сколько раз рецепт был добавлен в избранное."""
        return obj.favorited_by.count()


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
