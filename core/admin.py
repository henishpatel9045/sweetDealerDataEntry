from decimal import Decimal
from typing import Any
from django.contrib import admin
from django.contrib.admin.views.main import ChangeList
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.html import format_html
from core.changelists import ItemChangeList, OrderChangeList

from core.constants import ITEM_NAMES
from core.filters import BillBookFilter, DealerFilter
from core.forms import OrderForm

from .models import Order, Item, Stock

admin.site.site_header = "Vadiparti Yuvak Mandal"
admin.site.site_title = "Vadiparti Yuvak Mandal"


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = (
        "bill",
        "customer",
        "dealer_detail",
        "bill_total",
        "received",
        # "amount_to_collect",
        "isDispatched",
    )
    autocomplete_fields = ("dealer",)
    search_fields = (
        "bill_number",
        "customer_name",
    )
    actions = (
        "dispatch_orders",
        "calculate_totals",
    )
    list_filter = (BillBookFilter, DealerFilter, "dispatched")
    fieldsets = (
        (
            "Customer Details",
            {
                # "classes": ("collapse",),
                "fields": (
                    ("dealer", "bill_number"),
                    "customer_name",
                    "date",
                    ("total_amount", "amount_paid", "amount_received"),
                    "dispatched",
                ),
            },
        ),
        (
            "Item Details",
            {
                "classes": (
                    "wide",
                    "extrapretty",
                ),
                "fields": (
                    ("kaju_katri_500", "kaju_katri_1000"),
                    ("magaj_500", "magaj_1000"),
                    ("premium_mohanthal_500", "premium_mohanthal_1000"),
                    ("special_toparapak_500", "special_toparapak_1000"),
                    ("barfi_500", "barfi_1000"),
                    ("mava_mix_mithai_500", "mava_mix_mithai_1000"),
                    ("dry_fruite_biscuite_500", "dry_fruite_biscuite_1000"),
                    ("surti_chavanu_500", "surti_chavanu_1000"),
                    ("son_papdi_500", "son_papdi_1000"),
                ),
            },
        ),
    )

    @admin.action(description="Dispatch Orders")
    def dispatch_orders(self, request, queryset):
        errors = []
        for order in queryset:
            try:
                order.dispatched = True
                order.save()
            except Exception as e:
                errors.append(str(e))
        if errors:
            self.message_user(request, "\n".join(errors))
        else:
            self.message_user(request, "Orders dispatched successfully")

    @admin.action(description="Calculate Totals")
    def calculate_totals(self, request, queryset):
        errors = []
        for order in queryset:
            try:
                order.save()
            except Exception as e:
                errors.append(str(e))
        if errors:
            self.message_user(request, "\n".join(errors))
        else:
            self.message_user(request, "Totals calculated successfully")

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("dealer")

    def get_changelist(self, request, **kwargs):
        if request.user.is_superuser:
            return OrderChangeList
        return super().get_changelist(request, **kwargs)

    def bill(self, obj):
        if hasattr(obj, "amount_to_collect"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;">{obj.bill}</div>'
            )
        return obj.bill_number

    def customer(self, obj):
        if hasattr(obj, "amount_to_collect"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;"></div>'
            )
        return obj.customer_name

    def isDispatched(self, obj):
        if hasattr(obj, "amount_to_collect"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;"></div>'
            )
        return format_html(
            "<img src='/static/admin/img/icon-yes.svg' alt='True'>"
            if obj.dispatched
            else "<img src='/static/admin/img/icon-no.svg' alt='False'>"
        )

    def bill_total(self, obj):
        if hasattr(obj, "amount_to_collect"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;">{obj.bill_total}</div>'
            )
        return obj.total_amount

    def received(self, obj):
        if hasattr(obj, "amount_to_collect"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;">{obj.received}</div>'
            )
        return obj.amount_received

    def amount_to_collect(self, obj):
        if hasattr(obj, "amount_to_collect"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;">{obj.amount_to_collect}</div>'
            )
        return obj.total_amount - obj.amount_received

    def dealer_detail(self, obj):
        if hasattr(obj, "amount_to_collect"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;"></div>'
            )
        return f"{obj.dealer.name} - {obj.dealer.username}"

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("dealer")


class StockAdminInline(admin.TabularInline):
    model = Stock
    extra = 1
    fields = (
        "date",
        "box_500",
        "box_1000",
    )


@admin.register(Item)
class ItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "item_name",
        "quantity_available",
        "box_500_gm",
        "box_500_ready",
        "dispatched_500_gm",
        "box_1_kg",
        "box_1000_ready",
        "dispatched_1_kg",
        "quantity_ordered",
    )
    inlines = [StockAdminInline]

    def get_changelist(self, request, **kwargs):
        return ItemChangeList

    def changelist_view(self, request):
        self.orders = Order.objects.all().values_list(*ITEM_NAMES[1])
        return super().changelist_view(request)

    def item_name(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                '<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">Totals</div>'
            )
        return obj.name

    def box_500_ready(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">{obj.box_500_done}</div>'
            )
        return obj.box_500_ready

    def dispatched_500_gm(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">{obj.box_dispatched_500}</div>'
            )
        return obj.box_dispatched_500

    def box_1000_ready(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">{obj.box_1000_done}</div>'
            )
        return obj.box_1000_ready

    def dispatched_1_kg(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                f'<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">{obj.box_dispatched_1000}</div>'
            )
        return obj.box_dispatched_1000

    def quantity_available(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                '<div class="custom-row" style="font-size: 1.5rem; font-weight: bold;"></div>'
            )
        return str(obj.current_quantity) + " KGs"

    def get_item_index(self, item):
        for index, i in enumerate(ITEM_NAMES[1]):
            if item.lower().replace(" ", "_") in i:
                return index
        return -1

    def quantity_ordered(self, obj):
        if hasattr(obj, "quantity_ordered"):
            return format_html(
                '<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">%s KGs</div>'
                % obj.quantity_ordered
            )
        total = float(self.box_500_gm(obj)) * 0.5 + float(self.box_1_kg(obj))
        return str(total) + " KGs"

    def box_500_gm(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                '<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">%s</div>'
                % obj.box_500_gm
            )
        ind = self.get_item_index(obj.name)
        total = sum(i[ind] for i in self.orders)
        return str(total)

    def box_1_kg(self, obj):
        if hasattr(obj, "box_1_kg"):
            return format_html(
                '<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">%s</div>'
                % obj.box_1_kg
            )
        ind = self.get_item_index(obj.name) + 1
        total = sum(i[ind] for i in self.orders)
        return str(total)


class DispatchModel(Order):
    class Meta:
        proxy = True
        verbose_name = "Dispatch"
        verbose_name_plural = "Dispatches"


@admin.register(DispatchModel)
class DispatchModelAdmin(admin.ModelAdmin):
    list_display = (
        "bill_number",
        "customer_name",
        "dealer_detail",
        "total_amount",
        "amount_paid",
        "amount_to_collect",
        "amount_received",
        "dispatched",
    )
    search_fields = (
        "bill_number",
        "customer_name",
    )
    list_filter = (
        BillBookFilter,
        DealerFilter,
        "dispatched",
    )
    list_editable = (
        "amount_received",
        "dispatched",
    )

    def dealer_detail(self, obj):
        return f"{obj.dealer.name} - {obj.dealer.username}"

    def amount_to_collect(self, obj):
        return obj.total_amount - obj.amount_received
