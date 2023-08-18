"""
Serializers for the Budget APIs.
"""
from rest_framework import serializers

from core.models import (
    Budget,
    Category,
    Transaction,
)


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for categories."""

    class Meta:
        model = Category
        fields = ["id", "user", "name", "category_type"]
        read_only_fields = ["id", "user"]


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for the transactions."""

    class Meta:
        model = Transaction
        fields = ["id", "budget", "category", "amount", "notes"]
        read_only_fields = ["id", "budget"]


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budgets."""

    class Meta:
        model = Budget
        fields = ["id", "user", "currency", "balance"]
        read_only_fields = ["id", "user"]


class BudgetDetailSerializer(BudgetSerializer):
    class Meta(BudgetSerializer.Meta):
        fields = BudgetSerializer.Meta.fields
