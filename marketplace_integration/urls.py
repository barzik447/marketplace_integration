from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularSwaggerView,
    SpectacularRedocView,
    SpectacularAPIView,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/orders/", include("orders.urls")),
    path("auth/", include("user_auth.urls")),
    path("api/schema", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/swagger", SpectacularSwaggerView.as_view(url_name="schema")),
    path("api/docs/redoc", SpectacularRedocView.as_view(url_name="schema")),
]
