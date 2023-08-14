"""
Tests for models.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase

from core import models


def create_user(email="user@example.com", password="testpass123"):
    return get_user_model().objects.create_user(email=email, password=password)


def create_budget(user, balance, currency="UAH"):
    return models.Budget.objects.create(user=user, currency=currency, balance=balance)


def create_category(user, cashflow_type: str, name="default_value"):
    return models.Category.objects.create(
        user=user,
        name=name,
        category_type=cashflow_type,
    )


class ModelTests(TestCase):
    """Test models."""

    def test_create_user_with_email_successful(self):
        """Test creating a user with an email is successful."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new user."""
        sample_emails = [
            ["test1@EXAMPLE.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(
                email=email,
                password="testpass123",
            )
            self.assertEqual(user.email, expected)

    def test_create_superuser(self):
        """Test creating a superuser is successful."""
        user = get_user_model().objects.create_superuser(
            email="admin@example.com",
            password="testpass123",
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_budget_successful(self):
        """Test creating an account is successful."""
        user = create_user()
        budget = models.Budget.objects.create(
            user=user,
            currency="UAH",
            balance=1500,
        )

        self.assertEqual(budget.currency, "UAH")

    def test_create_category_successful(self):
        """Test creating a category is successful."""
        user = create_user()
        category = models.Category.objects.create(
            user=user,
            name="Rent",
            category_type="Income",
        )

        self.assertEqual(category.name, "Rent")

    def test_create_transaction_successful(self):
        """Test creating a transaction is successful."""
        user = create_user()
        budget = create_budget(user, 1500)
        category = create_category(user, "Income")

        transaction = models.Transaction.objects.create(
            budget=budget,
            category=category,
            amount=200,
            notes="Sample note",
        )

        self.assertEqual(transaction.budget, budget)
        self.assertEqual(transaction.category, category)
        self.assertEqual(transaction.amount, 200)
