from typing import Any
from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from core.constants import BILL_PER_BOOK
from core.models import Order
from django.utils.html import format_html
from import_export.admin import ImportExportModelAdmin

from .resources import CustomUserResource
from custom_auth.models import CustomUser as User, UserDeposit
from .forms import UserAdminChangeForm, UserAdminCreationForm


class UserDepositInline(admin.TabularInline):
    model = UserDeposit
    extra = 0


class UserAdmin(BaseUserAdmin, ImportExportModelAdmin):
    form = UserAdminChangeForm
    add_form = UserAdminCreationForm
    resource_classes = [CustomUserResource]
    inlines = [UserDepositInline]

    list_display = (
        "username",
        "name",
        "bill_books",
        "bill_range",
        "total_orders",
        "total_bill_amount",
        "total_amount",
        "amount_received",
        "amount_to_collect",
    )
    list_filter = ()
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            "Personal info",
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "total_amount",
                    # "amount_received",
                    "books",
                    "is_dealer",
                ),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_staff",
                    "groups",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
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
        self.transactions = UserDeposit.objects.all().values_list("user", "amount")
        return super().changelist_view(request)

    def amount_to_collect(self, obj):
        return (
            str(
                int(obj.total_amount)
                - int(self.amount_received(obj).split()[0])
            )
            + " ₹"
        )

    def amount_received(self, obj):
        total = sum(
            map(lambda x: x[1], filter(lambda x: x[0] == obj.pk, self.transactions))
        )
        return str(total) + " ₹"

    def bill_books(self, obj):
        res = ""
        for i in obj.books:
            res += "<div>" + str(i) + "</div>"
        return format_html(res)

    def bill_range(self, obj):
        bills = [
            f"{(book-1)*BILL_PER_BOOK + 1} - {book*BILL_PER_BOOK}" for book in obj.books
        ]
        res = ""
        for i in bills:
            res += "<div>" + i + "</div>"
        return format_html(res)

    def total_orders(self, obj):
        total = len(list(filter(lambda x: x[0] == obj.pk, self.orders)))
        return total

    def total_bill_amount(self, obj):
        total = sum(map(lambda x: x[1], filter(lambda x: x[0] == obj.pk, self.orders)))
        return str(total) + " ₹"

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        try:
            return super().save_model(request, obj, form, change)
        except Exception as e:
            msg = format_html(f'{e.args[0]} <a href="{request.path}">Open Form</a>')
            return messages.error(request, msg)


admin.site.register(User, UserAdmin)
