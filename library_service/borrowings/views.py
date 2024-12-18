from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils.timezone import now

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)


class BorrowingViewSet(viewsets.ModelViewSet):
    queryset = Borrowing.objects.select_related("book", "user")
    filterset_fields = ["is_active"]

    @action(detail=True, methods=["POST"])
    def return_borrowing(self, request, pk=None):
        borrowing = self.get_object()

        if borrowing.actual_return_date:
            return Response(
                {"error": "This borrowing has already been returned."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if request.user != borrowing.user and not request.user.is_staff:
            return Response(
                {"error": "You do not have permission to return this borrowing."},
                status=status.HTTP_403_FORBIDDEN,
            )

        borrowing.actual_return_date = now().date()
        borrowing.save()

        borrowing.book.inventory += 1
        borrowing.book.save()

        return Response(
            {"message": "Borrowing returned successfully."},
            status=status.HTTP_200_OK,
        )


    def get_serializer_class(self):
        if self.action == "list":
            return BorrowingListSerializer
        if self.action == "retrieve":
            return BorrowingDetailSerializer
        if self.action == "create":
            return BorrowingCreateSerializer
        if self.action == "return_borrowing":
            return BorrowingReturnSerializer
        return BorrowingSerializer

    def get_permissions(self):
        return [IsAuthenticated()]

    def get_queryset(self):
        user = self.request.user

        queryset = Borrowing.objects.select_related("book", "user")

        if not user.is_staff:
            queryset = queryset.filter(user=user)

        is_active = self.request.query_params.get("is_active")
        if is_active is not None:
            if is_active.lower() == "true":
                queryset = queryset.filter(actual_return_date__isnull=True)
            elif is_active.lower() == "false":
                queryset = queryset.filter(actual_return_date__isnull=False)

        user_id = self.request.query_params.get("user_id")
        if user.is_staff and user_id:
            queryset = queryset.filter(user_id=user_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
