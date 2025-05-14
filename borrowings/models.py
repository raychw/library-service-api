from django.db import models
from django.db.models import Q, F

from books.models import Book
from users.models import User


class Borrowing(models.Model):
    borrow_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=Q(expected_return_date__gt=F("borrow_date")),
                name="expected_return_after_borrow",
            ),
            models.CheckConstraint(
                check=Q(actual_return_date__gte=F("borrow_date"))
                | Q(actual_return_date__isnull=True),
                name="actual_return_after_borrow",
            ),
        ]

    def __str__(self):
        return f"Borrowing #{self.id} - {self.book.title}"
