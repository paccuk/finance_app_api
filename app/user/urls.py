"""
URL mapping for the user API.
"""
from django.urls import path


from . import views

app_name = "user"
urlpatterns = [
    path("me/", views.ManageUserView.as_view(), name="me"),
    path("create/", views.CreateUserView.as_view(), name="create"),
]
