import os
import requests
from datetime import date
from dotenv import load_dotenv

from borrowings.models import Borrowing

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_message(text: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as error:
        print(f"Error sending message: {error}")

def check_overdue_borrowings() -> None:
    today = date.today()

    overdue_borrowings = Borrowing.objects.filter(
        expected_return_date__lte=today, actual_return_date__isnull=True,
    )

    if overdue_borrowings.exists():
        for borrowing in overdue_borrowings:
            user = borrowing.user
            book = borrowing.book

            text = (
                f"Overdue borrowing!\n\n"
                f"User: {user.first_name} {user.last_name}\n"
                f"Book: \"{book.title}\"\n\n"
                f"Expected return date: {borrowing.expected_return_date.strftime('%d/%m/%Y')}"
            )
            send_telegram_message(text)
    else:
        send_telegram_message("No borrowings overdue today!")
