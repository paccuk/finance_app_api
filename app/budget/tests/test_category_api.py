"""
Tests for the categories API.
"""
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from core.models import Category

from budget.serializers import CategorySerializer

CATEGORIES_URL = reverse("budget:category-list")


def get_detail_url(category_id):
    return reverse("budget:category-detail", args=[category_id])


def create_user(email: str, password: str):
    return get_user_model().objects.create_user(email=email, password=password)


def create_category(user, **params):
    """user, name, category_type"""
    defaults = {
        "name": "Deposit",
        "category_type": "Income",
    }

    defaults.update(params)

    category = Category.objects.create(user=user, **params)
    return category


class PublicCategoriesAPITest(TestCase):
    """Test unauthenticated API requests."""

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateCategoryAPITest(TestCase):
    """Test authenticated API requests."""

    def setUp(self) -> None:
        self.user = create_user(email="user@example.com", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_categories_successful(self):
        Category.objects.create(user=self.user, name="Deposit", category_type="Income")
        Category.objects.create(user=self.user, name="Work", category_type="Income")

        res = self.client.get(CATEGORIES_URL)

        categories = Category.objects.all().order_by("-name")
        serializer = CategorySerializer(categories, many="True")

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_categories_limited_to_user_successful(self):
        other_user = create_user(email="other@example.com", password="testpass123")
        create_category(user=other_user, name="Rent", category_type="Expense")

        category = create_category(
            user=self.user, name="Spotify Premium", category_type="Expense"
        )
        res = self.client.get(CATEGORIES_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]["name"], category.name)
        self.assertEqual(res.data[0]["category_type"], category.category_type)
        self.assertEqual(res.data[0]["id"], category.id)

    def test_update_category_successful(self):
        category = create_category(
            user=self.user, name="Spotify Premium", category_type="Expense"
        )
        payload = {"name": "YouTube Premium"}
        url = get_detail_url(category.id)
        res = self.client.patch(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        category.refresh_from_db()
        self.assertEqual(category.name, payload["name"])

    def test_delete_category_successful(self):
        category = create_category(
            user=self.user, name="Spotify Premium", category_type="Expense"
        )
        url = get_detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        categories = Category.objects.filter(user=self.user)
        self.assertFalse(categories.exists())

    def test_delete_other_user_category_error(self):
        new_user = create_user(email="user2@example.com", password="testpass123")
        category = create_category(
            user=new_user, name="Spotify Premium", category_type="Expense"
        )

        url = get_detail_url(category.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Category.objects.filter(id=category.id).exists())
