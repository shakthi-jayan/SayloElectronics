from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    action = models.CharField(max_length=255)
    model = models.CharField(max_length=100)
    record_id = models.PositiveIntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.action} {self.model} #{self.record_id}"