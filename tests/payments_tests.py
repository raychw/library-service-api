import pytest
from django.core.exceptions import ValidationError

from tests.conftest import MAIN_URL
from payments.models import Payment


@pytest.mark.django_db
def test_payment_status_pending_or_paid(payment) -> None:
    payment.status = "Invalid"
    with pytest.raises(ValidationError):
        payment.full_clean()
        payment.save()


@pytest.mark.django_db
def test_payment_type_payment_or_fine(payment) -> None:
    payment.type = "Invalid"
    with pytest.raises(ValidationError):
        payment.full_clean()
        payment.save()


@pytest.mark.django_db
def test_payment_str(payment) -> None:
    assert str(payment) == f"Payment #{payment.id}: {payment.amount} - {payment.status}"


@pytest.mark.django_db
def test_payment_must_have_borrowing_attached(payment) -> None:
    payment.borrowing = None
    with pytest.raises(ValidationError):
        payment.full_clean()
        payment.save()


@pytest.mark.django_db
def test_payment_must_have_session_url(payment) -> None:
    payment.session_url = ""
    with pytest.raises(ValidationError):
        payment.full_clean()
        payment.save()


@pytest.mark.django_db
def test_payment_must_have_session_id(payment) -> None:
    payment.session_id = ""
    with pytest.raises(ValidationError):
        payment.full_clean()
        payment.save()


@pytest.mark.django_db
def test_payment_created_upon_new_borrowing(book, user, client) -> None:
    client.force_authenticate(user)
    assert (
        client.post(
            f"{MAIN_URL}/borrowings/",
            data={"book": book.id, "expected_return_date": "2025-02-02"},
        ).status_code
        == 201
    )
    assert Payment.objects.count() == 1


@pytest.mark.django_db
def test_fine_payment_created_for_overdue_borrowing(borrowing, client, user) -> None:
    borrowing.borrow_date = "2024-12-20"
    borrowing.expected_return_date = "2024-12-30"
    borrowing.save()
    client.force_authenticate(user)
    assert (
        client.post(
            f"{MAIN_URL}/borrowings/{borrowing.id}/return_borrowing/"
        ).status_code
        == 400
    )
    assert Payment.objects.count() == 1
