from orders.models import (
    Order,
    OrderMarketplace,
    OrderProduct,
    Product,
    OrderAmazonFake,
    OrderAliexpressFake,
)

from rest_framework import serializers


class OrderMarketplaceSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model = OrderMarketplace
        exclude = ["url_marketplace"]


class OrderProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderProduct
        exclude = ["order"]


class OrderSerializer(serializers.ModelSerializer):
    marketplaces = OrderMarketplaceSerializer(many=True, read_only=True)
    items = OrderProductSerializer(many=True, read_only=False, source="order_items")

    class Meta:
        model = Order
        exclude = ["products"]
        read_only_fields = ["price"]

    def create(self, validated_data):
        all_price = 0
        items = validated_data.pop("order_items")
        for item in items:
            price = item["product"].price * item["units"]
            all_price += price
        validated_data["price"] = all_price

        order = super().create(validated_data=validated_data)

        for item in items:
            OrderProduct.objects.create(order=order, **item)

        OrderAmazonFake.objects.create(order=order)
        OrderAliexpressFake.objects.create(order=order)

        return order


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = "__all__"
        read_only_fields = ["id"]
        # extra_kwargs = {"id": {"read_only": True}}
