from decimal import Decimal
from django.contrib import admin
from django.http.request import HttpRequest
from django.template.response import TemplateResponse
from django.db.models import Sum, F

from .models import Order, Item

admin.site.site_header = "Vadiparti Yuvak Mandal"
admin.site.site_title = "Vadiparti Yuvak Mandal"


@admin.register(Order)
class OrderModelAdmin(admin.ModelAdmin):
    list_display = ("id",)


@admin.register(Item)
class ItemModelAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "quantity_available",
        "quantity_ordered",
    )

    def changelist_view(self, request):
        self.ordered_quantity = (
            Order.objects.all()
            .annotate(
                kaju_katri=F("kaju_katri_500") * Decimal("0.5") + F("kaju_katri_1000"),
                magaj=F("magaj_500") * Decimal("0.5") + F("magaj_1000"),
                premium_mohanthal=F("premium_mohanthal_500") * Decimal("0.5")
                + F("premium_mohanthal_1000"),
                special_toparapak=F("special_toparapak_500") * Decimal("0.5")
                + F("special_toparapak_1000"),
                barfi=F("barfi_500") * Decimal("0.5") + F("barfi_1000"),
                mava_mix_mithai=F("mava_mix_mithai_500") * Decimal("0.5")
                + F("mava_mix_mithai_1000"),
                dry_fruite_biscuite=F("dry_fruite_biscuite_500") * Decimal("0.5")
                + F("dry_fruite_biscuite_1000"),
                surti_chavanu=F("surti_chavanu_500") * Decimal("0.5")
                + F("surti_chavanu_1000"),
                son_papdi=F("son_papdi_500") * Decimal("0.5"),
            )
            .aggregate(
                kaju_katri_sum=Sum("kaju_katri"),
                magaj_sum=Sum("magaj"),
                premium_mohanthal_sum=Sum("premium_mohanthal"),
                special_toparapak_sum=Sum("special_toparapak"),
                barfi_sum=Sum("barfi"),
                mava_mix_mithai_sum=Sum("mava_mix_mithai"),
                dry_fruite_biscuite_sum=Sum("dry_fruite_biscuite"),
                surti_chavanu_sum=Sum("surti_chavanu"),
                son_papdi_sum=Sum("son_papdi"),
            )
        )
        return super().changelist_view(request)

    def quantity_available(self, obj):
        return str(obj.current_quantity) + " KGs"

    def quantity_ordered(self, obj):
        total = self.ordered_quantity.get(
            obj.name.replace(" ", "_").lower() + "_sum", 0
        )

        return str(total) + " KGs"
