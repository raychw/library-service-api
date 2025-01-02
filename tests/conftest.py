import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from books.models import Book

User = get_user_model()

MAIN_URL = "http://127.0.0.1:8000/api/library_service"


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def user() -> User:
    return User.objects.create_user(
        email="testuser@test.com",
        first_name="Test",
        last_name="User",
        password="testpassword"
    )


@pytest.fixture
def admin() -> User:
    return User.objects.create_superuser(
        email="testsuperuser@test.com", password="testpassword"
    )


@pytest.fixture
def book() -> Book:
    return Book.objects.create(
        title="Test Book",
        author="Test Author",
        cover=Book.CoverType.HARD,
        daily_fee=1.00,
    )
