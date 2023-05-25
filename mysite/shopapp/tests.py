from string import ascii_letters

from random import choices
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase

from .models import Product, Order
from .utils import add_two_numbers


class AddTwoNumbersTestCase(TestCase):
    def test_add_two_numbers(self):
        result = add_two_numbers(4, 3)
        self.assertEqual(result, 7)


class ProductCreateTestCase(TestCase):
    def setUp(self) -> None:
        self.product_name = "".join(choices(ascii_letters, k=10))
        Product.objects.filter(name=self.product_name).delete()

    def test_create_product(self):
        response = self.client.post(reverse("shopapp:product_create"),
                         {
                             "name": self.product_name,
                             "price": "123.45",
                             "description": "A good table from wood",
                             "discount": "10",
                         }
                         )
        self.assertRedirects(response, reverse("shopapp:products_list"))
        self.assertTrue(
            Product.objects.filter(name=self.product_name).exists()
        )


class ProductDetailsViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.product = Product.objects.create(name="Best Product")

    @classmethod
    def tearDownClass(cls):
        cls.product.delete()

    def test_get_product(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_get_product_and_check_content(self):
        response = self.client.get(
            reverse("shopapp:product_details", kwargs={"pk": self.product.pk})
        )
        self.assertContains(response, self.product.name)


class ProductsListViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_products(self):
        response = self.client.get(reverse("shopapp:products_list"))
        self.assertQuerysetEqual(
            qs=Product.objects.filter(archived=False).all(),
            values=(p.pk for p in response.context["products"]),
            transform=lambda p: p.pk,
        )
        self.assertTemplateUsed(response, "shopapp/products-list.html")


class OrdersListViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="UserTest", password="12345")

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_orders_view(self):
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertContains(response, "Orders")

    def test_orders_view_anonymous(self):
        self.client.logout()
        response = self.client.get(reverse("shopapp:order_list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


class ProductsExportViewTestCase(TestCase):
    fixtures = [
        "products-fixture.json",
    ]

    def test_get_products_view(self):
        response = self.client.get(reverse("shopapp:products-export"))
        self.assertEqual(response.status_code, 200)
        products = Product.objects.order_by("pk").all()
        for product in products:
            print(product.pk, product.name)
        expected_data = [
            {
                "pk": product.pk,
                "name": product.name,
                "price": str(product.price),
                "archived": product.archived,
            }
            for product in products
        ]
        products_data = response.json()
        self.assertEqual(
            products_data["products"],
            expected_data,
        )


class OrderDetailViewTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="UserTest", password="12345")
        # permission = Permission.objects.get(name="Can view order")
        cls.user.user_permissions.set([32, ])  # id посмотрел в таблице auth_permission

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)
        self.order = Order.objects.create(delivery_address="ul. Lenina, 26", user=self.user, promocode="test10")
        self.order.products.set(Product.objects.filter(archived=False).all())

    def tearDown(self) -> None:
        self.order.delete()

    def test_order_details(self):
        response = self.client.get(
            reverse("shopapp:order_details", kwargs={"pk": self.order.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.order.delivery_address)  # адрес
        self.assertContains(response, self.order.promocode)  # промокод
        self.assertEqual(response.context["order"].pk, self.order.pk)  # первичный ключ в контексте ответа


class OrdersExportTestCase(TestCase):
    fixtures = [
        "shopapp/fixtures/products-fixture.json",
        "shopapp/fixtures/users-fixture.json",
        "shopapp/fixtures/orders-fixture.json"
    ]

    @classmethod
    def setUpClass(cls):
        cls.user = User.objects.create_user(username="UserTest", password="12345678")
        cls.user.is_staff = True
        cls.user.save()

    @classmethod
    def tearDownClass(cls):
        cls.user.delete()

    def setUp(self) -> None:
        self.client.force_login(self.user)

    def test_get_orders_view(self):
        response = self.client.get(reverse("shopapp:orders-export"))
        self.assertEqual(response.status_code, 200)
        orders = Order.objects.order_by("pk").all()
        expected_data = [
            {
                "pk": order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products_id": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        orders_data = response.json()
        self.assertEqual(
            orders_data["orders"],
            expected_data,
        )
