"""
Serializers for the Budget APIs.
"""
from rest_framework import serializers

from core.models import (
    Budget,
)


class BudgetSerializer(serializers.ModelSerializer):
    """Serializer for Budgets."""

    class Meta:
        model = Budget
        fields = ["id", "currency", "balance"]
        read_only_fields = ["id"]

    def create(self, validated_data):
        budget = Budget.objects.create(**validated_data)
        return budget

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class BudgetDetailSerializer(BudgetSerializer):
    class Meta(BudgetSerializer.Meta):
        fields = BudgetSerializer.Meta.fields
