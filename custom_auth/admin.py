from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from custom_auth.models import CustomUser as User

from .forms import UserAdminChangeForm, UserAdminCreationForm


class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = (
        "id",
        "username",
        "name",
        "is_dealer",
    )
    list_filter = ()
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("name", "is_dealer")},
        ),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "password",
                    "name",
                ),
            },
        ),
    )

    search_fields = (
        "username",
        "name",
    )
    ordering = ("username", "name")


admin.site.register(User, UserAdmin)
