from .views import OrderDetailsView, OrdersView, ProductDetailView, ProductsView
from django.urls import path

urlpatterns = [
    path("", OrdersView.as_view(), name="orders"),
    path("<int:pk>", OrderDetailsView.as_view(), name="orders_detail"),
    path("products", ProductsView.as_view(), name="products"),
    path("products/<int:pk>", ProductDetailView.as_view(), name="product_detail"),
]
