"""
Django admin customization.
"""
from django.contrib import admin

from . import models

admin.site.register(models.Budget)
admin.site.register(models.Category)
admin.site.register(models.Transaction)
