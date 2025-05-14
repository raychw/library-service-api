from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer
from payments.serializers import PaymentSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    payments = PaymentSerializer(many=True, read_only=True, source="payment_set")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingListSerializer(serializers.ModelSerializer):
    book = serializers.CharField(source="book.title", read_only=True)
    user = serializers.CharField(source="user.full_name", read_only=True)
    payments = serializers.StringRelatedField(source="payment_set", many=True)

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingDetailSerializer(serializers.ModelSerializer):
    book = BookSerializer()
    user = serializers.CharField(source="user.full_name", read_only=True)
    payments = PaymentSerializer(many=True, read_only=True, source="payment_set")

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
            "payments",
        )


class BorrowingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "book",
            "expected_return_date",
        )

    def validate(self, attrs):
        book = attrs.get("book")

        if book.inventory == 0:
            raise serializers.ValidationError(
                {"book": "This book is currently unavailable."}
            )

        return attrs

    def create(self, validated_data):
        book = validated_data["book"]

        if book.inventory <= 0:
            raise serializers.ValidationError({"book": "This book is out of stock."})

        book.inventory -= 1
        book.save()

        user = self.context["request"].user
        validated_data["user"] = user

        borrowing = Borrowing.objects.create(**validated_data)

        return borrowing


class BorrowingReturnSerializer(BorrowingSerializer):
    class Meta:
        model = Borrowing
        fields = ()
