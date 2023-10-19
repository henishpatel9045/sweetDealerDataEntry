from typing import Any
from django import forms

from core.constants import ITEM_NAMES
from .models import Order


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(OrderForm, self).__init__(*args, **kwargs)

        # Iterate through all fields in the form and add the 'form-control' class
        for field_name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"
            field.widget.attrs["id"] = field_name
            field.widget.attrs["type"] = "text"
            if field_name in ITEM_NAMES[1]:
                field.widget.attrs[
                    "style"
                ] = "width: 100%; padding: 0; padding-right: 0.3rem; text-align: right;"
