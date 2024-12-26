from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django_q.tasks import schedule
from django_q.models import Schedule
from django.utils import timezone
from datetime import timedelta


class BorrowingsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "borrowings"

    def ready(self):
        post_migrate.connect(schedule_overdue_check)


@receiver(post_migrate)
def schedule_overdue_check(sender, **kwargs):
    if sender.name == "borrowings":
        if not Schedule.objects.filter(func="borrowings.utils.check_overdue_borrowings").exists():
            schedule(
                "borrowings.utils.check_overdue_borrowings",
                schedule_type="D",
                next_run=timezone.now() + timedelta(seconds=10),
            )
