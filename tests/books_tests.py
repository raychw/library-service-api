import pytest
from decimal import Decimal
from django.core.exceptions import ValidationError

from tests.conftest import MAIN_URL


@pytest.mark.django_db
def test_only_positive_book_inventory(book) -> None:
    book.inventory = -1
    with pytest.raises(ValidationError):
        book.full_clean()
        book.save()


@pytest.mark.django_db
def test_daily_fee_minimal_value(book) -> None:
    book.daily_fee = Decimal(0.05)
    with pytest.raises(ValidationError):
        book.full_clean()
        book.save()


@pytest.mark.django_db
def test_book_str(book) -> None:
    assert str(book) == book.title


@pytest.mark.django_db
def test_book_ordering(book) -> None:
    assert book._meta.ordering == ["title"]


@pytest.mark.django_db
def test_book_cover_only_hard_or_soft(book) -> None:
    with pytest.raises(ValidationError):
        book.cover = "Newcover"
        book.full_clean()
        book.save()



@pytest.mark.django_db
def test_regular_user_can_list_and_retrieve(book, user, client) -> None:
    client.force_authenticate(user)
    assert client.get(f"{MAIN_URL}/books/").status_code == 200
    assert client.get(f"{MAIN_URL}/books/{book.id}/").status_code == 200


@pytest.mark.django_db
def test_regular_user_readonly(book, user, client) -> None:
    client.force_authenticate(user)
    for method in ["post", "put", "patch", "delete"]:
        assert getattr(client, method)(f"{MAIN_URL}/books/{book.id}/", data={}).status_code == 403


@pytest.mark.django_db
def test_admin_can_modify_books(book, admin, client) -> None:
    client.force_authenticate(admin)
    assert client.patch(f"{MAIN_URL}/books/{book.id}/", data={"title": "New Title"}).status_code == 200
    assert client.delete(f"{MAIN_URL}/books/{book.id}/").status_code == 204
