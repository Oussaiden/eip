from django.contrib import admin
from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['titre', 'user', 'type', 'lue', 'created_at']
    list_filter = ['type', 'lue']
    search_fields = ['titre', 'user__username']
    ordering = ['-created_at']
