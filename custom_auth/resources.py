from import_export import resources
from import_export.fields import Field

from core.models import Order

from .models import CustomUser, UserDeposit


class DummyUser:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
        self.pk = 0

    def __str__(self):
        return f"{self.username} - {self.name}"


class CustomUserResource(resources.ModelResource):
    def filter_export(self, queryset, *args, **kwargs):
        queryset = queryset.filter(is_dealer=True)
        return super().filter_export(queryset, *args, **kwargs)

    def before_export(self, queryset, *args, **kwargs):
        self.orders = Order.objects.all().values_list(
            "dealer",
            "total_amount",
        )
        self.transactions = UserDeposit.objects.all().values_list("user", "amount")
        return super().before_export(queryset, *args, **kwargs)

    class Meta:
        model = CustomUser
        fields = (
            "username",
            "name",
            "books",
            "total_orders",
            "site_total_amount",
            "total_amount",
            "amount_received",
            "amount_to_collect",
        )
        export_order = (
            "name",
            "username",
            "books",
            "total_orders",
            "site_total_amount",
            "total_amount",
            "amount_received",
            "amount_to_collect",
        )

    username = Field(attribute="username", column_name="Phone Number")
    name = Field(attribute="name", column_name="Name")
    books = Field(attribute="books", column_name="Books")
    total_orders = Field(column_name="Total Orders")
    amount_received = Field(column_name="Amount Received")
    total_amount = Field(attribute="total_amount", column_name="Total Amount")
    site_total_amount = Field(column_name="Total Site Amount")
    amount_to_collect = Field(column_name="Amount to Collect")

    def dehydrate_books(self, user):
        return "\n".join([str(book) for book in user.books])

    def dehydrate_total_amount(self, user):
        return str(user.total_amount) + " ₹"

    def dehydrate_site_total_amount(self, user):
        total = sum(map(lambda x: x[1], filter(lambda x: x[0] == user.pk, self.orders)))
        return str(total) + " ₹"

    def dehydrate_amount_received(self, user):
        total = sum(
            map(lambda x: x[1], filter(lambda x: x[0] == user.pk, self.transactions))
        )
        return str(total) + " ₹"

    def dehydrate_total_orders(self, user):
        total = len(list(filter(lambda x: x[0] == user.pk, self.orders)))
        return total

    def dehydrate_amount_to_collect(self, user):
        total = user.total_amount
        received = sum(
            map(lambda x: x[1], filter(lambda x: x[0] == user.pk, self.transactions))
        )
        return str(total - received) + " ₹"
