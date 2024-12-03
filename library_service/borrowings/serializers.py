from rest_framework import serializers

from borrowings.models import Borrowing
from books.serializers import BookSerializer


class BorrowingListSerializer(serializers.ModelSerializer):
    book_title = serializers.CharField(
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


class BorrowingDetailSerializer(serializers.ModelSerializer):
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
