from django.urls import path, include
from rest_framework.routers import DefaultRouter

from payments.views import PaymentViewSet


router = DefaultRouter()
router.register("", PaymentViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
