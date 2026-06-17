from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("Zusätzliche Felder", {"fields": ("birthdate", "address")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("Zusätzliche Felder", {"fields": ("birthdate", "address")}),)


delete
