from django.contrib import admin
from .models import AdminLog

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'action', 'model', 'record_id', 'timestamp')
    list_filter = ('model', 'action', 'user')
    search_fields = ('user__username', 'action', 'model')
    readonly_fields = ('user', 'action', 'model', 'record_id', 'timestamp')