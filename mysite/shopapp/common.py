from typing import Sequence
from csv import DictReader
from io import TextIOWrapper

from django.contrib.auth.models import User

from shopapp.models import Product, Order


def safe_csv_products(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)

    products = [
        Product(**row)
        for row in reader
    ]
    Product.objects.bulk_create(products)
    return products


def safe_csv_orders(file, encoding):
    csv_file = TextIOWrapper(
        file,
        encoding,
    )
    reader = DictReader(csv_file)
    orders = []
    for row in reader:
        user = User.objects.get(id=row.get("user"))
        order, created = Order.objects.get_or_create(
            delivery_address=row.get("delivery_address"),
            promocode=row.get("promocode"),
            user=user,
        )
        products: Sequence[Product] = Product.objects.only("id").filter(id__in=row.get("products").split(","))
        for product in products:
            order.products.add(product)
        orders.append(order)
    return orders
