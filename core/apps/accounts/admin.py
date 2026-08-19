# core/apps/accounts/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.accounts.models import OTP, Profile, User


class UserAdmin(BaseUserAdmin):
    ordering = ["phone_number"]
    list_display = ["phone_number", "email", "is_verified", "is_staff", "is_active"]
    list_filter = ["is_staff", "is_active", "is_verified", "type"]
    search_fields = ["phone_number", "email"]

    fieldsets = (
        (None, {"fields": ("phone_number", "password")}),
        ("Personal info", {"fields": ("email",)}),
        (
            "Permissions",
            {
                "fields": (
                    "type",
                    "is_active",
                    "is_verified",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "created_date", "updated_date")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("phone_number", "password1", "password2"),
            },
        ),
    )
    readonly_fields = ["created_date", "updated_date", "last_login"]


@admin.register(User)
class UserAdminModel(UserAdmin):
    pass


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "get_fullname"]
    search_fields = ["first_name", "last_name", "user__phone_number"]


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = [
        "phone_number",
        "purpose",
        "is_used",
        "attempts",
        "created_date",
        "expires_at",
    ]
    list_filter = ["purpose", "is_used"]
    readonly_fields = ["code", "created_date"]
