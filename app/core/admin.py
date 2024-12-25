from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseAdmin

from core import models


class UserAdmin(BaseAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )


admin.site.register(models.User, UserAdmin)
