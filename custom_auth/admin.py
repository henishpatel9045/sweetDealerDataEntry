from typing import Any
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core.models import Order
from django.utils.html import format_html
from custom_auth.models import CustomUser as User

from .forms import UserAdminChangeForm, UserAdminCreationForm



class UserAdmin(BaseUserAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm

    list_display = (
        "id",
        "username",
        "name",
        "books",
        "is_dealer",
        "total_orders",
        "total_amount",
    )
    list_filter = ()
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {"fields": ("name", "books", "is_dealer")},
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
                    "books",
                ),
            },
        ),
    )

    search_fields = (
        "username",
        "name",
    )
    ordering = ("username", "name")

    def changelist_view(self, request):
        self.orders = (
            Order.objects.all()
            .prefetch_related("dealer")
            .values_list("dealer", "total_amount", "amount_paid")
        )
        return super().changelist_view(request)

    def total_orders(self, obj):
        total = len(list(filter(lambda x: x[0] == obj.pk, self.orders)))
        return total

    def total_amount(self, obj):
        total = sum(map(lambda x: x[1], filter(lambda x: x[0] == obj.pk, self.orders)))
        return str(total) + " ₹"

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        try:
            return super().save_model(request, obj, form, change)
        except Exception as e:
            msg = format_html(f'{e.args[0]} <a href="{request.path}">Open Form</a>')
            return messages.error(request, msg)
            

admin.site.register(User, UserAdmin)
