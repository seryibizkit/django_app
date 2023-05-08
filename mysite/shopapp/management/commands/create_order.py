from django.core.management import BaseCommand
from django.contrib.auth.models import User
from shopapp.models import Order


class Command(BaseCommand):
    def handle(self, *args, **options):
        self.stdout.write("Create order")
        user = User.objects.get(username="admin")
        order = Order.objects.get_or_create(
            delivery_address="ul Mira, d 25",
            promocode="SALE25",
            user=user,
        )
        self.stdout.write("Created order {}".format(order))
