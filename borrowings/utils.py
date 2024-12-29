import os
import requests
import stripe
from django.conf import settings
from django.http import HttpResponse
from datetime import date
from dotenv import load_dotenv
from decimal import Decimal
from rest_framework import status

from borrowings.models import Borrowing
from payments.models import Payment

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

stripe.api_key = settings.STRIPE_SECRET_KEY

def send_telegram_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "HTML"}
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error sending message: {error}")


def check_overdue_borrowings() -> None:
    today = date.today()

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today,
        actual_return_date__isnull=True,
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user = borrowing.user
            book = borrowing.book

            text = (
                f"Overdue borrowing!\n\n"
                f"User: {user.first_name} {user.last_name}\n"
                f'Book: "{book.title}"\n\n'
                f"Expected return date: {borrowing.expected_return_date.strftime('%d/%m/%Y')}"
            )
            send_telegram_message(text)
    else:
        send_telegram_message("No borrowings overdue today!")


def create_stripe_payment_session(borrowing):
    try:
        borrowing_duration = (borrowing.expected_return_date - borrowing.borrow_date).days
        total_price = borrowing.book.daily_fee * borrowing_duration
        unit_amount = int(total_price * 100)

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {
                            "name": f"Borrowing #{borrowing.id} - {borrowing.book.title}",
                        },
                        "unit_amount": unit_amount,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://127.0.0.1:8000/api/library_service/payments/success",
            cancel_url="http://127.0.0.1:8000/api/library_service/payments/cancel",
        )

        payment = Payment.objects.create(
            session_id=session.id,
            session_url=session.url,
            amount=Decimal(total_price),
            status=Payment.PaymentStatus.PENDING,
            type=Payment.PaymentType.PAYMENT,
            borrowing=borrowing,
        )

        return payment
    except Exception as e:
        raise RuntimeError(f"Error creating Stripe Payment Session: {e}")
