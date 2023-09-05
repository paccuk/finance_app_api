"""
Views for the budgets API.
"""
from decimal import Decimal
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

from rest_framework_simplejwt.authentication import JWTAuthentication

from rest_framework.permissions import IsAuthenticated
from rest_framework import (
    viewsets,
    mixins,
)

from core.models import (
    Budget,
    Category,
    Transaction,
)


from . import serializers


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                "balance",
                OpenApiTypes.STR,
                description="Number to filter by balances",
            ),
            OpenApiParameter(
                "balance_range",
                OpenApiTypes.STR,
                description="Range of transaction amount values to filter\
                             (min, max) (min,) (, max)",
            ),
            OpenApiParameter(
                "currencies",
                OpenApiTypes.STR,
                description="Comma separated list of currency Enums to filter",
            ),
        ]
    )
)
class BudgetViewSet(viewsets.ModelViewSet):
    """View for manage budget APIs."""

    serializer_class = serializers.BudgetDetailSerializer
    queryset = Budget.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_decimal(self, qs):
        return Decimal(str(qs))

    def _params_to_upper_str_list(self, qs):
        return [value.strip().upper() for value in qs.split(",")]

    def _get_balance_range_filtered_queryset(self, queryset, balance_range):
        _balance_range = [value.strip() for value in balance_range.split(",")]

        if len(_balance_range) == 2 and "" not in _balance_range:
            _lrc = [Decimal(value) for value in _balance_range]
            return queryset.filter(balance__range=_lrc)

        if _balance_range[0] != "":
            return queryset.filter(balance__gte=Decimal(_balance_range[0]))

        if _balance_range[1] != "":
            return queryset.filter(balance__lte=Decimal(_balance_range[1]))

        raise ValueError("Range should contain exactly two values")

    def get_queryset(self):
        balance = self.request.query_params.get("balance")
        currencies = self.request.query_params.get("currencies")
        balance_range = self.request.query_params.get("balance_range")

        queryset = self.queryset

        if balance_range:
            queryset = self._get_balance_range_filtered_queryset(
                queryset, balance_range
            )

        if balance:
            _balance = self._params_to_decimal(balance)
            queryset = queryset.filter(balance=_balance)

        if currencies:
            currencies_list = self._params_to_upper_str_list(currencies)
            queryset = queryset.filter(currency__in=currencies_list)

        return queryset.filter(user=self.request.user).order_by("-id").distinct()

    def get_serializer_class(self):
        if self.action == "list":
            return serializers.BudgetSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class BaseBudgetAttrViewSet(
    mixins.DestroyModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Base ViewSet for budget attributes."""

    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]


@extend_schema(
    tags=["category"],
    parameters=[
        OpenApiParameter(
            "user",
            OpenApiTypes.STR,
            description="Comma separated list of user IDs to filter",
        )
    ],
)
class CategoryViewSet(BaseBudgetAttrViewSet):
    """Manage categories in the database."""

    serializer_class = serializers.CategorySerializer
    queryset = Category.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .order_by("-name")
            .distinct()
        )


@extend_schema(
    tags=["transaction"],
)
class TransactionViewSet(BaseBudgetAttrViewSet):
    """Manage transactions in the database."""

    serializer_class = serializers.TransactionSerializer
    queryset = Transaction.objects.all()

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(budget__user=self.request.user)
            .order_by("-created")
            .distinct()
        )
