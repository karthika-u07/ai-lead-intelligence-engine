from django.contrib import admin
from .models import Lead

@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "company", "email", "status", "created_at")
    search_fields = ("name", "email", "company")
    list_filter = ("status",)