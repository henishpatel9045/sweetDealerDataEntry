from django.contrib.admin.views.main import ChangeList
from django.db.models import Sum, F, Avg

from core.constants import ITEM_NAMES
from .models import Item, Order, Stock


class ItemChangeList(ChangeList):
    # provide the list of fields that we need to calculate averages and totals
    fields_to_total = [
        "box_500_gm",
        "box_1_kg",
        "quantity_ordered",
        "box_500_ready",
        "box_1000_ready",
        "box_500_dispatched",
        "box_1000_dispatched",
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
        stock = Stock.objects.all().values_list("box_500", "box_1000")
        total.box_500_done = str(sum(i[0] for i in stock))
        total.box_1000_done = str(sum(i[1] for i in stock))
        dispatched =  Item.objects.all().aggregate(total_500=Sum("box_dispatched_500"), total_1000=Sum("box_dispatched_1000"))
        total.box_dispatched_500 = str(dispatched["total_500"])
        total.box_dispatched_1000 = str(dispatched["total_1000"])
        return total

    def get_results(self, request):
        """
        The model admin gets queryset results from this method
        and then displays it in the template
        """
        super(ItemChangeList, self).get_results(request)
        # first get the totals from the current changelist
        total = self.get_total_values()
        # small hack. in order to get the objects loaded we need to call for
        # queryset results once so simple len function does it
        len(self.result_list)
        # and finally we add our custom rows to the resulting changelist
        self.result_list._result_cache.append(total)


class OrderChangeList(ChangeList):
    fields_to_total = [
        "total_orders",
        "total_amount",
        "amount_submitted",
        "remaining_amount",
    ]

    def get_total_values(self, all=False):
        """
        Get the totals
        """
        # basically the total parameter is an empty instance of the given model
        total = Order()
        total.bill = ("Sum " if all else "") + "Total"
        orders = (Order.objects.all() if all else self.queryset).values_list(
            "total_amount", "amount_received"
        )
        total_amount = sum(i[0] for i in orders)
        amount_submitted = sum(i[1] for i in orders)
        remaining_amount = total_amount - amount_submitted
        total.bill_total = total_amount
        total.received = amount_submitted
        total.amount_to_collect = remaining_amount
        return total

    def get_results(self, request):
        """
        The model admin gets queryset results from this method
        and then displays it in the template
        """
        super(OrderChangeList, self).get_results(request)
        # first get the totals from the current changelist
        total = self.get_total_values(all=True)
        request_total = self.get_total_values()

        # small hack. in order to get the objects loaded we need to call for
        # queryset results once so simple len function does it
        len(self.result_list)
        # and finally we add our custom rows to the resulting changelist
        self.result_list._result_cache.insert(0, total)
        self.result_list._result_cache.insert(1, request_total)
