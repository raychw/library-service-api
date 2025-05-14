import pytest
from django.core.exceptions import ValidationError

from tests.conftest import MAIN_URL


@pytest.mark.django_db
def test_expected_return_date_cannot_be_set_before_borrow_date(borrowing) -> None:
    borrowing.expected_return_date = "2020-01-01"
    with pytest.raises(ValidationError):
        borrowing.full_clean()
        borrowing.save()


@pytest.mark.django_db
def test_actual_return_date_cannot_be_set_before_borrow_date(borrowing) -> None:
    borrowing.actual_return_date = "2020-01-01"
    with pytest.raises(ValidationError):
        borrowing.full_clean()
        borrowing.save()


@pytest.mark.django_db
def test_borrowing_str(borrowing) -> None:
    assert str(borrowing) == f"Borrowing #{borrowing.id} - {borrowing.book.title}"


@pytest.mark.django_db
def test_cannot_borrow_unavailable_book(borrowing, book, user, client) -> None:
    book.inventory = 0
    book.save()
    client.force_authenticate(user)
    assert (
        client.post(
            f"{MAIN_URL}/borrowings/",
            data={"book": book.id, "expected_return_date": "2025-02-02"},
        ).status_code
        == 400
    )


@pytest.mark.django_db
def test_regular_user_cannot_modify_borrowings(borrowing, user, client) -> None:
    client.force_authenticate(user)
    for method in ["post", "put", "patch", "delete"]:
        assert (
            getattr(client, method)(
                f"{MAIN_URL}/borrowings/{borrowing.id}/", data={}
            ).status_code
            == 405
        )


@pytest.mark.django_db
def test_user_cannot_see_other_users_borrowings(borrowing, user, admin, client) -> None:
    borrowing.user = admin
    borrowing.save()
    client.force_authenticate(user)
    assert client.get(f"{MAIN_URL}/borrowings/{borrowing.id}/").status_code == 404


@pytest.mark.django_db
def test_admin_can_see_all_borrowings(borrowing, user, admin, client) -> None:
    borrowing.user = user
    client.force_authenticate(admin)
    assert client.get(f"{MAIN_URL}/borrowings/").status_code == 200
    assert client.get(f"{MAIN_URL}/borrowings/{borrowing.id}/").status_code == 200


@pytest.mark.django_db
def test_return_borrowing(borrowing, user, client) -> None:
    client.force_authenticate(user)
    assert (
        client.post(
            f"{MAIN_URL}/borrowings/{borrowing.id}/return_borrowing/"
        ).status_code
        == 200
    )
    borrowing.refresh_from_db()
    assert borrowing.actual_return_date is not None


@pytest.mark.django_db
def test_cannot_return_returned_borrowing(borrowing, user, client) -> None:
    borrowing.borrow_date = "2024-12-20"
    borrowing.expected_return_date = "2024-12-30"
    borrowing.actual_return_date = "2025-01-02"
    borrowing.save()
    client.force_authenticate(user)
    assert (
        client.post(
            f"{MAIN_URL}/borrowings/{borrowing.id}/return_borrowing/"
        ).status_code
        == 400
    )


@pytest.mark.django_db
def test_book_inventory_increases_after_return(book, borrowing, user, client) -> None:
    book.inventory = 1
    book.save()
    borrowing.book = book
    borrowing.save()
    client.force_authenticate(user)
    assert (
        client.post(
            f"{MAIN_URL}/borrowings/{borrowing.id}/return_borrowing/"
        ).status_code
        == 200
    )
    book.refresh_from_db()
    assert book.inventory == 2


@pytest.mark.django_db
def test_overdue_borrowing_fine(borrowing, user, client) -> None:
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
