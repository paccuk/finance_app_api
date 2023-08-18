"""
Database models.
"""

from decimal import Decimal
from django.conf import settings
from django.db import models

from .currency_choices import CURRENCY_CHOICES


class CommonInfo(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    objects = models.Manager()

    class Meta:
        ordering = ["-created"]
        abstract = True


class Budget(CommonInfo):
    """Budget of a specific user."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    currency = models.CharField(max_length=15, choices=CURRENCY_CHOICES, blank=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0"))

    def __str__(self):
        return "%s ID(%s)" % (self.user.email, self.pk)


class Category(CommonInfo):
    """Base model for income and expense categories."""

    CATEGORY_TYPES = [
        ("Income", "Income"),
        ("Expense", "Expense"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)
    category_type = models.CharField(max_length=7, choices=CATEGORY_TYPES, blank=False)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class Transaction(CommonInfo):
    """Represents budget transactions."""

    budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True)


# class Cashflow(CommonInfo):
#     """Base class for income and expense."""

#     budget = models.ForeignKey(Budget, on_delete=models.CASCADE)
#     category = models.ForeignKey(Category, on_delete=models.CASCADE)
#     amount = models.IntegerField()
#     notes = models.TextField()
