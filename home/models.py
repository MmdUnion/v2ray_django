from django.contrib.auth.models import User
from django.db import models


class UserConfigModel(models.Model):
    config_id = models.IntegerField()
    for_user = models.ForeignKey(User, on_delete=models.CASCADE)


    def __str__(self):
        return self.for_user.first_name



class TicketModel(models.Model):
    message_text = models.TextField()
    for_user = models.ForeignKey(User, on_delete=models.CASCADE)
    admin_seen = models.BooleanField(default=False)
    send_by_admin = models.BooleanField(default=False)
    user_seen = models.BooleanField(default=False)
    send_telegram_alert = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.for_user.first_name



 