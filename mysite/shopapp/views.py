from timeit import default_timer
import re

from django.contrib.auth.models import Group
from django.contrib.auth.mixins import LoginRequiredMixin, \
    PermissionRequiredMixin, UserPassesTestMixin
from django.http import HttpResponse, HttpRequest, HttpResponseRedirect
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


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = ["shopapp.add_product", ]
    model = Product
    fields = "name", "price", "description", "discount"
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = ["shopapp.change_product", ]
    permission_denied_message = "You are not allowed to edit this product"

    model = Product
    fields = "name", "price", "description", "discount"
    template_name_suffix = "_update_form"

    def form_valid(self, form):
        if self.object.created_by == self.request.user or self.request.user.is_superuser:
            self.object.save()
            success_url = self.get_success_url()
            return HttpResponseRedirect(success_url)
        else:
            return HttpResponseRedirect(reverse("shopapp:product_details", kwargs={"pk": self.object.pk}))

    def get_success_url(self):
        return reverse("shopapp:product_details", kwargs={"pk": self.object.pk})


class ProductDeleteView(PermissionRequiredMixin, DeleteView):
    permission_required = ["shopapp.delete_product", ]
    permission_denied_message = "You are not allowed to archive this product"
    model = Product
    success_url = reverse_lazy("shopapp:products_list")

    def form_valid(self, form):
        if self.object.created_by == self.request.user or self.request.user.is_superuser:
            success_url = self.get_success_url()
            self.object.archived = True
            self.object.save()
            return HttpResponseRedirect(success_url)
        return HttpResponseRedirect(reverse("shopapp:product_details", kwargs={"pk": self.object.pk}))

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
