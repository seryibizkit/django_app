from django import forms
from django.contrib.auth.models import Group

from .models import Product, Order


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = "name", "price", "description", "discount"  # , "created_by"


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = "user", "delivery_address", "products", "promocode"


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = "name",
