"""
Tests for the budget APIs.
"""
from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import (
    Budget,
)

from budget.serializers import (
    BudgetSerializer,
)

BUDGETS_URL = reverse("budget:budget-list")


def get_detail_url(budget_id):
    return reverse("budget:budget-detail", args=[budget_id])


def create_budget(user, **params):
    defaults = {
        "currency": "UAH",
        "balance": 5000,
    }
    defaults.update(params)

    budget = Budget.objects.create(user=user, **defaults)
    return budget


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicBudgetAPITest(TestCase):
    """Test unauthorized API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BUDGETS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateBudgetAPITest(TestCase):
    """Test authorized API requests."""

    def setUp(self) -> None:
        self.client = APIClient()
        self.user = create_user(email="user@example.com", password="testpass123")
        self.client.force_authenticate(self.user)

    def test_retrieve_budgets_successful(self):
        create_budget(self.user)
        create_budget(self.user)

        res = self.client.get(BUDGETS_URL)

        budgets = Budget.objects.all().order_by("-id")
        serializer = BudgetSerializer(budgets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_budget_limited_to_user_successful(self):
        other_user = create_user(email="other@example.com", password="testpass123")
        create_budget(other_user)
        create_budget(self.user)

        res = self.client.get(BUDGETS_URL)

        budgets = Budget.objects.filter(user=self.user)
        serializer = BudgetSerializer(budgets, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_budget_with_api_successful(self):
        payload = {
            "currency": "UAH",
            "balance": Decimal("50000"),
        }

        res = self.client.post(BUDGETS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        budget = Budget.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(budget, k), v)

        self.assertEqual(budget.user, self.user)

    def test_partial_update_successful(self):
        budget = create_budget(
            user=self.user,
            currency="UAH",
            balance=Decimal("50000"),
        )

        payload = {"balance": Decimal("60000")}
        url = get_detail_url(budget.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        budget.refresh_from_db()
        self.assertEqual(budget.currency, "UAH")
        self.assertEqual(budget.balance, payload["balance"])
        self.assertEqual(budget.user, self.user)

    def test_full_update_successful(self):
        budget = create_budget(
            user=self.user,
            currency="UAH",
            balance=Decimal("50000"),
        )

        payload = {
            "currency": "USD",
            "balance": Decimal("60000"),
        }

        url = get_detail_url(budget.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        budget.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(budget, k), v)
        self.assertEqual(budget.user, self.user)

    def test_update_user_error(self):
        new_user = create_user(email="user2@example.com", password="testpass123")
        budget = create_budget(user=self.user)

        payload = {"user": new_user.id}
        url = get_detail_url(budget.id)
        self.client.patch(url, payload)

        budget.refresh_from_db()
        self.assertEqual(budget.user, self.user)

    def test_delete_budget_successful(self):
        budget = create_budget(user=self.user)

        url = get_detail_url(budget.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Budget.objects.filter(id=budget.id).exists())

    def test_delete_other_user_budget_error(self):
        new_user = create_user(email="user2@example.com", password="testpass123")
        budget = create_budget(user=new_user)

        url = get_detail_url(budget.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Budget.objects.filter(id=budget.id).exists())
