from django.core.exceptions import ValidationError
from django.db import models
from decimal import Decimal


class Book(models.Model):
    class CoverType(models.TextChoices):
        HARD = "Hard"
        SOFT = "Soft"

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    cover = models.CharField(max_length=4, choices=CoverType.choices)
    inventory = models.PositiveIntegerField(default=0)
    daily_fee = models.DecimalField(max_digits=6, decimal_places=2,)

    class Meta:
        ordering = ["title"]

    def __str__(self):
        return self.title

    def clean(self):
        if self.daily_fee < Decimal("0.10"):
            raise ValidationError("Daily fee must be at least 0.10")
