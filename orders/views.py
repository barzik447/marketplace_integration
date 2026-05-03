from django.db import transaction
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateAPIView,
    RetrieveDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from orders.models import Order, Product
from orders.pagination import OrderPagination, ProductPagination
from orders.serializers import OrderSerializer, ProductSerializer
from orders.permisions import AdminCreatorPermision
from orders.tasks import send_order_marketplace


class OrdersView(ListCreateAPIView):
    queryset = Order.objects.all().order_by("id")
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = OrderPagination

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Order.objects.all()
        return Order.objects.filter(creator=self.request.user)

    def perform_create(self, serializer):
        new_order = serializer.save(creator=self.request.user)

        for marketplace in new_order.marketplaces.all():
            transaction.on_commit(
                lambda m=marketplace: send_order_marketplace.delay(m.id)
            )


class OrderDetailsView(RetrieveUpdateAPIView):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated, AdminCreatorPermision]
    serializer_class = OrderSerializer


class ProductsView(ListCreateAPIView):
    queryset = Product.objects.all().order_by("id")
    serializer_class = ProductSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ProductPagination


class ProductDetailView(RetrieveDestroyAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.all()
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        permissions = super().get_permissions()
        if self.request.method != "GET":
            permissions.append(IsAdminUser())
        return permissions
