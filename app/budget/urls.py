"""
URL mapping for the user API.
"""
from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register("budgets", views.BudgetViewSet)
router.register("categories", views.CategoryViewSet)
router.register("transactions", views.TransactionViewSet)

app_name = "budget"
urlpatterns = [
    path("", include(router.urls)),
]
