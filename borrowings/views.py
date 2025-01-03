from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import mixins
from django.utils.timezone import now
from drf_spectacular.utils import extend_schema

from borrowings.models import Borrowing
from payments.models import Payment
from borrowings.serializers import (
    BorrowingSerializer,
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingCreateSerializer,
    BorrowingReturnSerializer,
)
from borrowings.utils import send_telegram_message, create_stripe_payment_session


class BorrowingViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Borrowing.objects.select_related("book", "user")
    filterset_fields = ["is_active"]

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
        borrowing = serializer.save(user=self.request.user)
        user = borrowing.user
        book = borrowing.book

        create_stripe_payment_session(self.request, borrowing)

        message = f'{user.first_name} {user.last_name} has just borrowed "{book.title}"'
        send_telegram_message(message)

    @extend_schema(
        summary="Returns a borrowing",
        description="This endpoint returns a borrowing or displays an error if the borrowing can't be returned.",
        responses={200: str},
    )
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

        if Payment.objects.filter(
            borrowing=borrowing, status=Payment.PaymentStatus.PENDING
        ).exists():
            return Response(
                {
                    "error": "You have a pending payment, please complete it before returning the borrowing."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        borrowing.actual_return_date = now().date()
        borrowing.save()

        borrowing.book.inventory += 1
        borrowing.book.save()

        if borrowing.actual_return_date > borrowing.expected_return_date:
            create_stripe_payment_session(self.request, borrowing)

            return Response(
                {
                    "error": "You have returned the book late, please pay the fine attached to your borrowing."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(
            {"message": "Borrowing returned successfully."},
            status=status.HTTP_200_OK,
        )
