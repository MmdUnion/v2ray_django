from django.contrib import admin

from .models import TicketModel, UserConfigModel


class UserConfigAdmin(admin.ModelAdmin):
    list_display = ("for_user", "config_id")
    list_filter = ("for_user", "config_id")



class TicketAdmin(admin.ModelAdmin):
    list_display = ("for_user", "message_text", "admin_seen", "user_seen","created_at")
    list_filter = ("for_user", "admin_seen", "user_seen", "send_by_admin", "created_at")



admin.site.register(UserConfigModel, UserConfigAdmin)
admin.site.register(TicketModel, TicketAdmin)
