from django.contrib import admin

from .models import Recipe, Ingredient, Tag, ShoppingCart, Favorite


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'image',
        'name',
        'text',
        'cooking_time',
        'author',
        'short_link'
    )
    list_editable = (
        'name',
        'text',
        'cooking_time'
    )
    search_fields = ('name', 'author')
    list_filter = ('tags',)
    filter_horizontal = ('ingredients', 'tags')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient)
admin.site.register(Tag)
admin.site.register(ShoppingCart)
admin.site.register(Favorite)

