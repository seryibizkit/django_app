from typing import Sequence

from django.db import transaction
from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Order, Product


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write("Create order with products")
        user = User.objects.get(username="admin")
        # products: Sequence[Product] = Product.objects.defer("description", "price", "created_at").all()
        products: Sequence[Product] = Product.objects.only("id").all()
        order, created = Order.objects.get_or_create(
            delivery_address="ul. Moskovyan, d 21",
            promocode="promo4",
            user=user,
        )
        for product in products:
            order.products.add(product)
        self.stdout.write("Created order {}".format(order))
