from typing import Any
from django import forms
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
