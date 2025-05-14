from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import (
    PaymentViewSet,
    payment_success,
    canceled_payment,
)


router = DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("success", payment_success, name="payment-success"),
    path("cancel", canceled_payment, name="payment-cancel"),
]
