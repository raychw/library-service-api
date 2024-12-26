from rest_framework import viewsets

from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payment.objects.prefetch_related("borrowing")

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Payment.objects.select_related("borrowing", "user")

        if not user.is_staff:
            queryset = queryset.filter(user=user)
