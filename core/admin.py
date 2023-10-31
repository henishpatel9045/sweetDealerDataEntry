from decimal import Decimal
from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, F, Avg
from django.utils.html import format_html

from core.constants import ITEM_NAMES

from .models import Order, Item

admin.site.site_header = "Vadiparti Yuvak Mandal"
admin.site.site_title = "Vadiparti Yuvak Mandal"


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ("bill_number", "dealer_name", "dealer_phone")
    autocomplete_fields = ("dealer",)

    def get_queryset(self, request: HttpRequest) -> QuerySet[Any]:
        return super().get_queryset(request).prefetch_related("dealer")

    def dealer_name(self, obj):
        return obj.dealer.name

    def dealer_phone(self, obj):
        return obj.dealer.username


class TotalAveragesChangeList(ChangeList):
    # provide the list of fields that we need to calculate averages and totals
    fields_to_total = [
        "box_500_gm",
        "box_1_kg",
        "quantity_ordered",
    ]

    def get_total_values(self):
        """
        Get the totals
        """
        # basically the total parameter is an empty instance of the given model
        total = Item()
        total.name = "Totals"  # the label for the totals row
        orders = Order.objects.all().values_list(*ITEM_NAMES[1])
        total_500 = sum(
            i for order in orders for ind, i in enumerate(order) if ind % 2 == 0
        )
        total_1000 = sum(
            i for order in orders for ind, i in enumerate(order) if ind % 2 == 1
        )
        quantity_total = total_500 * 0.5 + total_1000
        total.box_500_gm = str(total_500)
        total.box_1_kg = str(total_1000)
        total.quantity_ordered = str(quantity_total)

        return total

    def get_results(self, request):
        """
        The model admin gets queryset results from this method
        and then displays it in the template
        """
        super(TotalAveragesChangeList, self).get_results(request)
        # first get the totals from the current changelist
        total = self.get_total_values()
        # small hack. in order to get the objects loaded we need to call for
        # queryset results once so simple len function does it
        len(self.result_list)
        # and finally we add our custom rows to the resulting changelist
        self.result_list._result_cache.append(total)


@admin.register(Item)
class ItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "item_name",
        "quantity_available",
        "box_500_gm",
        "box_1_kg",
        "quantity_ordered",
    )

    def get_changelist(self, request, **kwargs):
        return TotalAveragesChangeList

    def changelist_view(self, request):
        self.orders = Order.objects.all().values_list(*ITEM_NAMES[1])
        return super().changelist_view(request)

    def item_name(self, obj):
        if hasattr(obj, "box_500_gm"):
            return format_html(
                '<div class="custom-row" style="font-size: 1.5rem; font-weight: bolder;">Totals</div>'
            )
        return obj.name

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
