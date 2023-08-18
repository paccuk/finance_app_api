"""
Tests for the transactions APIs.
"""
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework.test import APIClient
from rest_framework import status

from core.models import (
    Budget,
    Category,
    Transaction,
)

from budget.serializers import TransactionSerializer

TRANSACTIONS_URL = reverse("budget:transaction-list")


def create_user(email, password):
    return get_user_model().objects.create_user(email=email, password=password)


def get_detail_url(transaction_url):
    return reverse("budget:transaction-detail", args=[transaction_url])


def create_category(user, name: str, c_type: str):
    return Category.objects.create(
        user=user,
        name=name,
        category_type=c_type,
    )


class PublicTransactionAPITest(TestCase):
    """Tests for unauthenticated user requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(TRANSACTIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateTransactionAPITest(TestCase):
    """Tests for authenticated user requests."""

    def setUp(self) -> None:
        self.user = create_user(email="user@example.com", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(self.user)
        self.budget = Budget.objects.create(
            user=self.user,
            currency="UAH",
            balance=Decimal("50000"),
        )

    def test_retrieve_transactions_successful(self):
        Transaction.objects.create(
            budget=self.budget,
            category=create_category(self.user, "Deposit", "Income"),
            amount=Decimal("5000"),
            notes="Monthly deposit income",
        )
        Transaction.objects.create(
            budget=self.budget,
            category=create_category(self.user, "Rent", "Expense"),
            amount=Decimal("-10000"),
            notes="Monthly rent",
        )

        res = self.client.get(TRANSACTIONS_URL)

        transactions = Transaction.objects.all().order_by("-created")
        serializer = TransactionSerializer(transactions, many="True")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_transaction_limited_to_budget_successful(self):
        other_budget = Budget.objects.create(
            user=create_user(email="other@example.com", password="testpass123"),
            currency="UAH",
            balance=Decimal("25000"),
        )
        Transaction.objects.create(
            budget=other_budget,
            category=create_category(self.user, "Deposit", "Income"),
            amount=Decimal("5000"),
            notes="Monthly deposit income",
        )
        transaction = Transaction.objects.create(
            budget=self.budget,
            category=create_category(self.user, "Work", "Income"),
            amount=Decimal("40000"),
            notes="Monthly work income",
        )

        res = self.client.get(TRANSACTIONS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(Decimal(res.data[0]["amount"]), transaction.amount)
        self.assertEqual(res.data[0]["notes"], transaction.notes)

    def test_update_transaction_successful(self):
        transaction = Transaction.objects.create(
            budget=self.budget,
            category=create_category(self.user, "Deposit", "Income"),
            amount=Decimal("5000"),
            notes="Monthly deposit income",
        )

        payload = {"notes": "Updated notes"}
        url = get_detail_url(transaction.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        transaction.refresh_from_db()
        self.assertEqual(transaction.notes, payload["notes"])

    def test_delete_transaction(self):
        transaction = Transaction.objects.create(
            budget=self.budget,
            category=create_category(self.user, "Deposit", "Income"),
            amount=Decimal("5000"),
            notes="Monthly deposit income",
        )

        url = get_detail_url(transaction.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        transactions = Transaction.objects.filter(budget=self.budget)
        self.assertFalse(transactions.exists())
