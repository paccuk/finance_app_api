"""
Views for the budgets API.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    viewsets,
)

from core.models import (
    Budget,
)

from . import serializers


class BudgetViewSet(viewsets.ModelViewSet):
    """View for manage budget APIs."""

    serializer_class = serializers.BudgetDetailSerializer
    queryset = Budget.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset
        return queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.BudgetSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
