from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import ShopUser


class ShopUserAdmin(UserAdmin):
    model = ShopUser
    list_display = (
        'email',
        'first_name',
        'last_name',
        'is_staff',
        'is_active',
    )
    list_filter = ('is_staff', 'is_active')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': ('first_name', 'last_name')}),
        (
            'Права доступа',
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                    'user_permissions',
                )
            },
        ),
    )

    search_fields = ('email',)
    ordering = ('email',)


admin.site.register(ShopUser, ShopUserAdmin)
