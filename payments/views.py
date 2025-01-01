import datetime

import stripe
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import JsonResponse

from payments.models import Payment
from payments.serializers import (
    PaymentSerializer,
    PaymentListSerializer,
    PaymentDetailSerializer,
)


class PaymentViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Payment.objects.prefetch_related("borrowing")

    def get_serializer_class(self):
        if self.action == "list":
            return PaymentListSerializer
        if self.action == "retrieve":
            return PaymentDetailSerializer
        return PaymentSerializer

    def get_queryset(self):
        user = self.request.user

        queryset = Payment.objects.prefetch_related("borrowing")

        if not user.is_staff:
            queryset = queryset.filter(user=user)
        return queryset


@api_view(["GET"])
def payment_success(request):
    session_id = request.GET.get("session_id")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        customer = request.user
        payment = get_object_or_404(Payment, session_id=session_id)

        if session.payment_status == "paid":
            payment.status = Payment.PaymentStatus.PAID
            payment.save()
            return Response(
                {
                    "message": "Payment successful",
                    "customer": {"id": customer.id, "name": customer.full_name},
                    "payment_status": "Paid",
                },
                status=status.HTTP_200_OK,
            )
        else:
            return JsonResponse({"error": "Payment not completed yet."}, status=400)

    except stripe.error.InvalidRequestError as e:
        return JsonResponse({"error": str(e)}, status=400)


@api_view(["GET"])
def canceled_payment(request):
    session_id = request.GET.get("session_id")
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        customer = request.user
        expiration = datetime.datetime.fromtimestamp(session.expires_at).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        return Response(
            {
                "message": "Payment canceled",
                "customer": {"id": customer.id, "name": customer.full_name},
                "session_expires_at": expiration,
            },
            status=status.HTTP_200_OK,
        )

    except stripe.error.InvalidRequestError as e:
        return JsonResponse({"error": str(e)}, status=400)
