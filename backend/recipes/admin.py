from django.contrib import admin

from .models import Recipe, Ingredient, Tag, ShoppingCart, Favorite


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


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)
