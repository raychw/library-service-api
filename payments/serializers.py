from rest_framework import serializers

from payments.models import Payment
from borrowings.serializers import BorrowingListSerializer


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "amount",
        )


class PaymentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "amount",
        )


class PaymentDetailSerializer(serializers.ModelSerializer):
    borrowing = BorrowingListSerializer()

    class Meta:
        model = Payment
        fields = (
            "id",
            "status",
            "type",
            "borrowing",
            "session_url",
            "session_id",
            "amount",
        )
