from decimal import Decimal
from django.db import models, transaction
from django.db.models import Sum, F
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.utils import timezone

from .constants import *

User = get_user_model()


class Item(models.Model):
    ITEM_CHOICES = [
        ("kaju_katri_500", "Kaju Katri 500g"),
        ("kaju_katri_1000", "Kaju Katri 1kg"),
        ("magaj_500", "Magaj 500g"),
        ("magaj_1000", "Magaj 1kg"),
        ("premium_mohanthal_500", "Premium Mohanthal 500g"),
        ("premium_mohanthal_1000", "Premium Mohanthal 1kg"),
        ("special_toparapak_500", "Special Toparapak 500g"),
        ("special_toparapak_1000", "Special Toparapak 1kg"),
        ("barfi_500", "Barfi 500g"),
        ("barfi_1000", "Barfi 1kg"),
        ("mava_mix_mithai_500", "Mava Mix Mithai 500g"),
        ("mava_mix_mithai_1000", "Mava Mix Mithai 1kg"),
        ("dry_fruite_biscuite_500", "Dry Fruite Biscuite 500g"),
        ("dry_fruite_biscuite_1000", "Dry Fruite Biscuite 1kg"),
        ("surti_chavanu_500", "Surti Chavanu 500g"),
        ("surti_chavanu_1000", "Surti Chavanu 1kg"),
        ("son_papdi_500", "Son Papdi 500g"),
        ("son_papdi_1000", "Son Papdi 1kg"),
    ]

    ITEM_NAMES = [
        ("Kaju Katri", "Kaju Katri"),
        ("Magaj", "Magaj"),
        ("Premium Mohanthal", "Premium Mohanthal"),
        ("Special Toparapak", "Special Toparapak"),
        ("Barfi", "Barfi"),
        ("Mava Mix Mithai", "Mava Mix Mithai"),
        ("Dry Fruite Biscuite", "Dry Fruite Biscuite"),
        ("Surti Chavanu", "Surti Chavanu"),
        ("Son Papdi", "Son Papdi"),
    ]

    name = models.CharField(max_length=200, unique=True, choices=ITEM_NAMES)
    current_quantity = models.DecimalField(
        max_digits=10, decimal_places=1, default=0, help_text="In KGs"
    )
    box_dispatched_500 = models.IntegerField(default=0)
    box_dispatched_1000 = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def box_500_ready(self):
        stock = Stock.objects.filter(item__pk=self.pk).aggregate(
            total=Sum("box_500")
        )["total"]
        return stock

    @property
    def box_1000_ready(self):
        stock = Stock.objects.filter(item__pk=self.pk).aggregate(
            total=Sum("box_1000")
        )["total"]
        return stock


class Stock(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    date = models.DateField(default=timezone.now)
    box_500 = models.IntegerField(default=0)
    box_1000 = models.IntegerField(default=0)

    def __str__(self) -> str:
        return str(self.date)


def update_item_model(item, box_500, box_1000, add=True):
    item = Item.objects.get(name=item)
    if add:
        item.box_dispatched_500 += box_500
        item.box_dispatched_1000 += box_1000
    else:
        item.box_dispatched_500 -= box_500
        item.box_dispatched_1000 -= box_1000
    item.save()


def update_item_stock(data: dict, add=True):
    for item in data.keys():
        update_item_model(item, data[item]["box_500"], data[item]["box_1000"], add=add)


class Order(models.Model):
    dealer = models.ForeignKey(User, on_delete=models.CASCADE)
    bill_number = models.IntegerField(unique=True, validators=[MinValueValidator(1)])
    customer_name = models.CharField(max_length=200, default="")
    date = models.DateField(default=timezone.now)
    kaju_katri_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Kaju Katri 500g",
    )
    kaju_katri_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Kaju Katri 1kg",
    )
    magaj_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Magaj 500g",
    )
    magaj_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Magaj 1kg",
    )
    premium_mohanthal_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Premium Mohanthal 500g",
    )
    premium_mohanthal_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Premium Mohanthal 1kg",
    )
    special_toparapak_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Special Toparapak 500g",
    )
    special_toparapak_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Special Toparapak 1kg",
    )
    barfi_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Barfi 500g",
    )
    barfi_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Barfi 1kg",
    )
    mava_mix_mithai_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Mava Mix Mithai 500g",
    )
    mava_mix_mithai_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Mava Mix Mithai 1kg",
    )
    dry_fruite_biscuite_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Dry Fruite Biscuite 500g",
    )
    dry_fruite_biscuite_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Dry Fruite Biscuite 1kg",
    )
    surti_chavanu_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Surti Chavanu 500g",
    )
    surti_chavanu_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Surti Chavanu 1kg",
    )
    son_papdi_500 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Son Papdi 500g",
    )
    son_papdi_1000 = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0, "Quantity can't be negative.")],
        verbose_name="Son Papdi 1kg",
    )
    total_amount = models.IntegerField(blank=True)
    amount_paid = models.IntegerField(
        default=0, blank=True, verbose_name="Advanced Collected"
    )
    dispatched = models.BooleanField(default=False)
    dispatched_date = models.DateField(blank=True, null=True)
    amount_received = models.IntegerField(default=0, blank=True)

    def check_quantity(self) -> bool:
        initial_quantity = Item.objects.all()

        quant = {i.name: i.current_quantity for i in initial_quantity}
        current_ordered_quantity = (
            Order.objects.prefetch_related("dealer")
            .exclude(pk=self.pk)
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
                son_papdi=F("son_papdi_500") * Decimal("0.5") + F("son_papdi_1000"),
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

        NAME_MAPPING = [
            ("Kaju Katri", "kaju_katri_sum", "kaju_katri_500", "kaju_katri_1000"),
            ("Magaj", "magaj_sum", "magaj_500", "magaj_1000"),
            (
                "Premium Mohanthal",
                "premium_mohanthal_sum",
                "premium_mohanthal_500",
                "premium_mohanthal_1000",
            ),
            (
                "Special Toparapak",
                "special_toparapak_sum",
                "special_toparapak_500",
                "special_toparapak_1000",
            ),
            ("Barfi", "barfi_sum", "barfi_500", "barfi_1000"),
            (
                "Mava Mix Mithai",
                "mava_mix_mithai_sum",
                "mava_mix_mithai_500",
                "mava_mix_mithai_1000",
            ),
            (
                "Dry Fruite Biscuite",
                "dry_fruite_biscuite_sum",
                "dry_fruite_biscuite_500",
                "dry_fruite_biscuite_1000",
            ),
            (
                "Surti Chavanu",
                "surti_chavanu_sum",
                "surti_chavanu_500",
                "surti_chavanu_1000",
            ),
            ("Son Papdi", "son_papdi_sum", "son_papdi_500", "son_papdi_1000"),
        ]

        for i in NAME_MAPPING:
            if (current_ordered_quantity[i[1]] or 0) + (
                Decimal(getattr(self, i[2])) * Decimal("0.5")
            ) + (Decimal(getattr(self, i[3]))) > quant[i[0]]:
                raise ValueError(f"Order limit exceeded for {i[0]}.")

    def calculate_total(self) -> int:
        total = 0
        total += self.kaju_katri_500 * KAJU_KATRI_500
        total += self.kaju_katri_1000 * KAJU_KATRI_1000
        total += self.magaj_500 * MAGAJ_500
        total += self.magaj_1000 * MAGAJ_1000
        total += self.premium_mohanthal_500 * PREMIUM_MOHANTHAL_500
        total += self.premium_mohanthal_1000 * PREMIUM_MOHANTHAL_1000
        total += self.special_toparapak_500 * SPECIAL_TOPARAPAK_500
        total += self.special_toparapak_1000 * SPECIAL_TOPARAPAK_1000
        total += self.barfi_500 * BARFI_500
        total += self.barfi_1000 * BARFI_1000
        total += self.mava_mix_mithai_500 * MAVA_MIX_MITHAI_500
        total += self.mava_mix_mithai_1000 * MAVA_MIX_MITHAI_1000
        total += self.dry_fruite_biscuite_500 * DRY_FRUITE_BISCUITE_500
        total += self.dry_fruite_biscuite_1000 * DRY_FRUITE_BISCUITE_1000
        total += self.surti_chavanu_500 * SURTI_CHAVANU_500
        total += self.surti_chavanu_1000 * SURTI_CHAVANU_1000
        total += self.son_papdi_500 * SON_PAPDI_500
        total += self.son_papdi_1000 * SON_PAPDI_1000
        return total

    def save(self):
        with transaction.atomic():
            flag = False
            for book in self.dealer.books:
                if (
                    self.bill_number > (book - 1) * BILL_PER_BOOK
                    and self.bill_number <= book * BILL_PER_BOOK
                ):
                    flag = True
                    break
            if not flag:
                raise ValueError("You are not assigned the book of this bill.")
            self.total_amount = self.calculate_total()
            if self.amount_paid > self.total_amount:
                raise ValueError("Amount paid can't be greater than total amount.")
            self.check_quantity()
            if self.pk is not None:
                current_order = Order.objects.get(pk=self.pk)
                data = {}
                for index, item in enumerate(ITEM_NAMES[0]):
                    data[item[0]] = {
                        "box_500": getattr(self, ITEM_NAMES[1][index * 2]),
                        "box_1000": getattr(self, ITEM_NAMES[1][index * 2 + 1]),
                    }
                if current_order.dispatched == False and self.dispatched:
                    update_item_stock(data)
                elif current_order.dispatched == True and self.dispatched == False:
                    update_item_stock(data, add=False)

            super().save()

    class Meta:
        ordering = [
            "bill_number",
        ]

    def __str__(self):
        return f"{self.bill_number}, Book-{self.bill_number // BILL_PER_BOOK + 1}"
