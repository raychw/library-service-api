from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingListSerializer(BorrowingSerializer):
    book = serializers.CharField(
        source="book.title", read_only=True
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingDetailSerializer(BorrowingSerializer):
    book = BookSerializer()
    user_email = serializers.CharField(
        source="user.email", read_only=True
    )

    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
        )


class BorrowingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Borrowing
        fields = (
            "id",
            "borrow_date",
            "expected_return_date",
            "actual_return_date",
            "book",
            "user",
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
            raise serializers.ValidationError({"book": "This book is currently unavailable."})

        return attrs

    def create(self, validated_data):
        book = validated_data["book"]
        book.inventory -= 1
        book.save()

        user = self.context["request"].user
        borrowing = Borrowing.objects.create(user=user, **validated_data)

        return borrowing
