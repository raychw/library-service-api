from datetime import timedelta
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.utils.timezone import now
from django_q.tasks import schedule
from django_q.models import Schedule


def schedule_overdue_check():
    if not Schedule.objects.filter(
        func="borrowings.utils.check_overdue_borrowings"
    ).exists():
        schedule(
            "borrowings.utils.check_overdue_borrowings",
            schedule_type=Schedule.DAILY,
            next_run=now() + timedelta(seconds=10),
        )


@receiver(post_migrate)
def on_post_migrate(sender, **kwargs):
    from django.db import connection

    try:
        if "django_q_schedule" in connection.introspection.table_names():
            schedule_overdue_check()
    except Exception as e:
        print(f"Error during task scheduling: {e}")
