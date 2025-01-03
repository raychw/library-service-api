from django.apps import AppConfig
from datetime import timedelta
from django.utils.timezone import now
from django.db.utils import OperationalError


def schedule_overdue_check():
    from django_q.models import Schedule
    from django_q.tasks import schedule

    if not Schedule.objects.filter(
        func="borrowings.utils.check_overdue_borrowings"
    ).exists():
        schedule(
            "borrowings.utils.check_overdue_borrowings",
            schedule_type="D",
            next_run=now() + timedelta(seconds=10),
        )


class BorrowingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings"

    def ready(self):
        from django.db import connection

        try:
            if "django_q_schedule" in connection.introspection.table_names():
                schedule_overdue_check()
        except OperationalError:
            pass
