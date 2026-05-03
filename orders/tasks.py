import httpx
from celery import shared_task

from orders.models import OrderMarketplace, OrderProduct
from orders.exceptions import ApiStatusException
from django.utils import timezone


def amazon_fake_data(
    marketplace: OrderMarketplace, products: list[OrderProduct]
) -> dict:
    return {
        "userId": marketplace.order.creator.id,
        "products": [
            {"id": product.product.id, "price": product.product.price}
            for product in products
        ],
    }


def aliexpress_fake_data(
    marketplace: OrderMarketplace, products: list[OrderProduct]
) -> dict:
    return {
        "user_id": marketplace.order.creator.id,
        "items": [
            {"product_id": product.product.id, "quantity": product.units}
            for product in products
        ],
    }


MARKETPLACE_DATA_FACTORY = {
    "AmazonFake": amazon_fake_data,
    "AliexpressFake": aliexpress_fake_data,
}


@shared_task(
    bind=True,
    autoretry_for=(ApiStatusException,),
    max_retries=4,
    retry_backoff=True,
)
def send_order_marketplace(self, order_marketplace_id: int):
    marketplace = (
        OrderMarketplace.objects.filter(id=order_marketplace_id)
        .select_related("order")
        .first()
    )
    products = marketplace.order.order_items.select_related("product").all()

    json_send = MARKETPLACE_DATA_FACTORY[marketplace.marketplace_name](
        marketplace, products
    )

    response: httpx.Response = getattr(httpx, marketplace.api_method)(
        marketplace.url_marketplace, json=json_send
    )

    if response.status_code == 201 or response.status_code == 200:
        marketplace.status = 1
        marketplace.date_success = timezone.now()
        marketplace.save()
        return

    if (
        response.status_code == 429 or response.status_code >= 500
    ) and self.request.retries < self.max_retries:
        raise ApiStatusException()

    marketplace.status = 2
    marketplace.date_error = timezone.now()
    marketplace.api_call_error_msg = response.text
    marketplace.save()
