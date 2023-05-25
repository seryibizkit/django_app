from timeit import default_timer
import re

from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect, JsonResponse
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import TemplateView, ListView, \
    DetailView, CreateView, UpdateView, DeleteView

from .models import Product, Order
from .forms import ProductForm, OrderForm, GroupForm


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
        }
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
    model = Product
    context_object_name = "product"


class ProductsListView(ListView):
    template_name = 'shopapp/products-list.html'
    # model = Product
    context_object_name = "products"
    queryset = Product.objects.filter(archived=False)


class ProductCreateView(CreateView):
    model = Product
    fields = "name", "price", "description", "discount"
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
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        created_by_current_user = self.get_object().created_by == self.request.user
        return has_edit_perm and created_by_current_user

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})


class ProductDeleteView(UserPassesTestMixin, DeleteView):
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def test_func(self):
        if self.request.user.is_superuser:
            return True
        has_edit_perm = self.request.user.has_perm("shopapp.change_product")
        created_by_current_user = self.get_object().created_by == self.request.user
        return has_edit_perm and created_by_current_user

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
