from django.contrib import admin

from .models import User, Subscribe


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email'
    )
    list_editable = (
        'first_name',
        'last_name',
    )
    search_fields = ('username', 'email')


admin.site.register(User, UserAdmin)
admin.site.register(Subscribe)
