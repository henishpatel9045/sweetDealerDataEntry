from django.contrib import admin

from core.constants import BILL_PER_BOOK


class InputFilter(admin.SimpleListFilter):
    template = "admin/input_filter.html"

    def lookups(self, request, model_admin):
        return ((),)

    def choices(self, changelist):
        # Grab only the "all" option.
        all_choice = next(super().choices(changelist))
        all_choice["query_parts"] = (
            (k, v)
            for k, v in changelist.get_filters_params().items()
            if k != self.parameter_name
        )
        yield all_choice


class BillBookFilter(InputFilter):
    title = "Bill Book Number"
    parameter_name = "book_number"

    def queryset(self, request, queryset):
        if self.value():
            book = int(self.value())
            return queryset.filter(
                bill_number__lte=book * BILL_PER_BOOK,
                bill_number__gt=(book - 1) * BILL_PER_BOOK,
            )
        return queryset


class DealerFilter(InputFilter):
    title = "Dealer Phone"
    parameter_name = "dealer_phone"

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                dealer__username=self.value(),
            )
        return queryset
