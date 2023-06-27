from django.urls import path, include
from django.views.decorators.cache import cache_page
from rest_framework.routers import DefaultRouter

from .views import create_order, \
    ShopIndexView, GroupListView, \
    ProductDetailsView, ProductsListView, \
    OrdersListView, OrderDetailView, ProductCreateView, \
    ProductUpdateView, ProductDeleteView, OrderUpdateView, \
    OrderDeleteView, OrderCreateView, ProductsExportView, \
    OrdersExportView, ProductViewSet, OrderViewSet,\
    LatestProductsFeed, UserOrdersListView, UserOrdersExportView

app_name = "shopapp"

routers = DefaultRouter()
routers.register("products", ProductViewSet)
routers.register("orders", OrderViewSet)

urlpatterns = [
    # path("", cache_page(60 * 2)(ShopIndexView.as_view()), name="index"),
    path("", ShopIndexView.as_view(), name="index"),
    path("api/", include(routers.urls)),
    path("groups/", GroupListView.as_view(), name="groups_list"),
    path("products/", ProductsListView.as_view(), name="products_list"),
    path("products/export/", ProductsExportView.as_view(), name="products-export"),
    path("products/<int:pk>/", ProductDetailsView.as_view(), name="product_details"),
    path("products/create/", ProductCreateView.as_view(), name="product_create"),
    path("products/<int:pk>/update", ProductUpdateView.as_view(), name="product_update"),
    path("products/<int:pk>/archive", ProductDeleteView.as_view(), name="product_delete"),
    path("products/latest/feed/", LatestProductsFeed(), name="products-feed"),
    path("orders/", OrdersListView.as_view(), name="order_list"),
    path("users/<int:user_id>/orders/export/", UserOrdersExportView.as_view(), name="user_orders_export"),
    path("orders/export/", OrdersExportView.as_view(), name="orders-export"),
    path("orders/<int:pk>/", OrderDetailView.as_view(), name="order_details"),
    path("users/<int:user_id>/orders", UserOrdersListView.as_view(), name="user_orders"),
    path("orders/create/", OrderCreateView.as_view(), name="order_create"),
    path("orders/<int:pk>/update", OrderUpdateView.as_view(), name="order_update"),
    path("orders/<int:pk>/delete", OrderDeleteView.as_view(), name="order_delete"),
]
