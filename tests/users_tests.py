import pytest
from django.core.exceptions import ValidationError

from tests.conftest import MAIN_URL


@pytest.mark.django_db
def test_first_name_and_last_name_are_required(user) -> None:
    user.first_name = ""
    user.last_name = ""
    with pytest.raises(ValidationError):
        user.full_clean()
        user.save()


@pytest.mark.django_db
def test_email_is_required(user) -> None:
    user.email = ""
    with pytest.raises(ValidationError):
        user.full_clean()
        user.save()


@pytest.mark.django_db
def test_user_str(user) -> None:
    assert str(user) == user.email


@pytest.mark.django_db
def test_user_full_name(user) -> None:
    assert user.full_name == f"{user.first_name} {user.last_name}"


@pytest.mark.django_db
def test_regular_user_is_not_staff(user) -> None:
    assert not user.is_staff
    assert not user.is_superuser


@pytest.mark.django_db
def test_user_cannot_change_their_id(user) -> None:
    user.id = 2
    with pytest.raises(ValidationError):
        user.full_clean()
        user.save()


@pytest.mark.django_db
def test_user_can_modify_their_credentials(user, client) -> None:
    client.force_authenticate(user)
    assert (
        client.patch(
            f"{MAIN_URL}/users/me/",
            data={"first_name": "New Name"},
            password="testpassword",
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"{MAIN_URL}/users/me/",
            data={"last_name": "New Last Name"},
            password="testpassword",
        ).status_code
        == 200
    )
    assert (
        client.patch(
            f"{MAIN_URL}/users/me/",
            data={"email": "newemail@test.com"},
            password="testpassword",
        ).status_code
        == 200
    )


@pytest.mark.django_db
def test_unauthorized_user_cannot_reach_profile(client) -> None:
    assert client.get(f"{MAIN_URL}/users/me/").status_code == 401


@pytest.mark.django_db
def test_anyone_can_register(client) -> None:
    assert (
        client.post(
            f"{MAIN_URL}/users/",
            data={
                "email": "testemail@test.com",
                "first_name": "Test",
                "last_name": "User",
                "password": "testpassword",
            },
        ).status_code
        == 201
    )
