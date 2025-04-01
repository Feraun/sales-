from django import forms
from .models import Order

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)]

class CartAddProductForm(forms.Form):
    quantity = forms.IntegerField(
        min_value = 0,
        initial=1,
        widget=forms.NumberInput(attrs={'class': 'quantity-input'})
    )

    override = forms.BooleanField(required=False,
                                  initial=False,
                                  widget=forms.HiddenInput)
