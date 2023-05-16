from django.urls import path

from .views import create_product, create_order, \
    ShopIndexView, GroupListView, \
    ProductDetailsView, ProductsListView, \
    OrdersListView, OrderDetailView

app_name = "shopapp"

urlpatterns = [
    path("", ShopIndexView.as_view(), name="index"),
    path("groups/", GroupListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/create/", create_product, name="product_create"),
    path("orders/", OrdersListView.as_view(), name="orders_list"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("orders/create/", create_order, name="order_create"),
]
