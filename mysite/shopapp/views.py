"""
В этом модуле лежат различные наборы представлений.

Разные views интернет-магазина: по товарам, заказам и т.д.
"""

import logging
from timeit import default_timer

from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpRequest,\
    HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, \
    DetailView, CreateView, UpdateView, DeleteView
from rest_framework.viewsets import ModelViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse

from .models import Product, Order, ProductImage
from .forms import ProductForm, OrderForm, GroupForm
from .serializers import ProductSerializer, OrderSerializer


log = logging.getLogger(__name__)


@extend_schema(description="Product views CRUD")
class ProductViewSet(ModelViewSet):
    """
    Набор представлений для действий над Product.

    Здесь полный CRUD для сущностей товара
    """

    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [
        SearchFilter,
        DjangoFilterBackend,
        OrderingFilter,
    ]
    ordering_fields = ["name", "price", "discount"]
    search_fields = ["name", "description"]
    filterset_fields = [
        "name",
        "description",
        "archived",
        "price",
        "discount",
    ]

    @extend_schema(
        summary="Get one product by ID",
        description="Retrieves **product**, returns 404 if not found",
        responses={
            200: ProductSerializer,
            404: OpenApiResponse(description="Empty response, product by id not found"),
        }
    )
    def retrieve(self, *args, **kwargs):
        return super().retrieve(*args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [
        DjangoFilterBackend,
        OrderingFilter,
    ]
    ordering_fields = ["created_at", "user"]
    filterset_fields = [
        "delivery_address",
        "promocode",
        "created_at",
        "user",
        "products",
    ]


class ShopIndexView(View):
    def get(self, request: HttpRequest) -> HttpResponse:
        products = [
            ("laptop", 1999),
            ("desktop", 2999),
            ("smartphone", 999)
        ]
        context = {
            "time_running": default_timer(),
            "products": products,
            "items": 1,
        }
        log.debug("Products for shop index: %s", products)
        log.info("Rendering shop index.")
        return render(request, "shopapp/shop-index.html", context=context)


class GroupListView(View):
    @classmethod
    def get(cls, request: HttpRequest) -> HttpResponse:
        context = {
            "form": GroupForm,
            "groups": Group.objects.prefetch_related('permissions').all(),
        }
        return render(request, 'shopapp/groups-list.html', context=context)

    @classmethod
    def post(cls, request: HttpRequest) -> HttpResponse:
        form = GroupForm(request.POST)
        if form.is_valid():
            form.save()

        return redirect(request.path)


class ProductDetailsView(DetailView):
    template_name = "shopapp/product-details.html"
    # model = Product
    queryset = Product.objects.prefetch_related("images")
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = "name", "price", "description", "discount", "preview"
    success_url = reverse_lazy("shopapp:products_list")


# class ProductCreateView(PermissionRequiredMixin, CreateView):
#     permission_required = ["shopapp.add_product", ]
#     model = Product
#     fields = "name", "price", "description", "discount"
#     success_url = reverse_lazy("shopapp:products_list")
#
#     def form_valid(self, form):
#         form.instance.created_by = self.request.user
#         return super().form_valid(form)


class ProductUpdateView(UserPassesTestMixin, UpdateView):
    model = Product
    # fields = "name", "price", "description", "discount", "preview"
    template_name_suffix = "_update_form"
    form_class = ProductForm

    def form_valid(self, form):
        response = super().form_valid(form)
        preview = form.cleaned_data["preview"]
        print(preview)
        for image in form.files.getlist("images"):
            ProductImage.objects.create(
                product=self.object,
                image=image,
            )
        return response

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        # created_by_current_user = self.get_object().created_by == self.request.user
        return has_edit_perm  # and created_by_current_user

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})


class ProductDeleteView(UserPassesTestMixin, DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        # created_by_current_user = self.get_object().created_by == self.request.user
        return has_edit_perm

    def form_valid(self, form):
        success_url = self.get_success_url()
        self.object.archived = True
        self.object.save()
        return HttpResponseRedirect(success_url)

# def create_product(request: HttpRequest) -> HttpResponse:
#     if request.method == "POST":
#         form = ProductForm(request.POST)
#         if form.is_valid():
#             # name = form.cleaned_data["name"]
#             # price = form.cleaned_data["price"]
#             # description = form.cleaned_data["description"]
#             # Product.objects.create(**form.cleaned_data)
#             form.save()
#             url = reverse("shopapp:products_list")
#             return redirect(url)
#     else:
#         form = ProductForm()
#     context = {
#         "form": form
#     }
#     return render(request, 'shopapp/create-product.html', context=context)


class OrdersListView(LoginRequiredMixin, ListView):
    queryset = (
        Order.objects.select_related("user").prefetch_related("products").all()
    )


class OrderDetailView(PermissionRequiredMixin, DetailView):
    permission_required = ["shopapp.view_order", ]
    template_name = "shopapp/order_details.html"
    queryset = (
        Order.objects.select_related("user").prefetch_related("products").all()
    )


class OrderUpdateView(UpdateView):
    model = Order
    fields = "user", "products", "delivery_address", "promocode"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("shopapp:order_details", kwargs={"pk": self.object.pk})


class OrderDeleteView(DeleteView):
    model = Order
    success_url = reverse_lazy("shopapp:order_list")


class OrderCreateView(CreateView):
    model = Order
    fields = "user", "products", "delivery_address", "promocode"
    success_url = reverse_lazy("shopapp:order_list")


def create_order(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            # name = form.cleaned_data["name"]
            # price = form.cleaned_data["price"]
            # description = form.cleaned_data["description"]
            # Product.objects.create(**form.cleaned_data)
            form.save()
            url = reverse("shopapp:orders_list")
            return redirect(url)
    else:
        form = OrderForm()
    context = {
        "form": form
    }
    return render(request, 'shopapp/create-order.html', context=context)


class ProductsExportView(View):
    @classmethod
    def get(cls, request: HttpRequest) -> HttpResponse:
        products = Product.objects.order_by("pk").all()
        products_data = [
            {
                'pk': product.pk,
                'name': product.name,
                'price': product.price,
                'archived': product.archived
            }
            for product in products
        ]
        elem = products_data[0]
        name = elem["name"]
        print("name:", name)
        return JsonResponse({"products": products_data})


class OrdersExportView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    @classmethod
    def get(cls, request: HttpRequest) -> HttpResponse:
        orders = Order.objects.order_by("pk").all()
        orders_data = [
            {
                'pk': order.pk,
                "delivery_address": order.delivery_address,
                "promocode": order.promocode,
                "user_id": order.user.pk,
                "products_id": [product.pk for product in order.products.all()],
            }
            for order in orders
        ]
        return JsonResponse({"orders": orders_data})
