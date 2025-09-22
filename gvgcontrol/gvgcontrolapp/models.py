from django.db import models
from django.utils import timezone
from datetime import timedelta

class AdminUser(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class Member(models.Model):
    nickname = models.CharField(max_length=50)
    discord_id = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=[('active', 'Active'), ('inactive', 'Inactive')])
    payment_method = models.CharField(max_length=50, choices=[('weekly', 'Weekly'), ('monthly', 'Monthly')])
    paid_at = models.DateTimeField(null=True, blank=True)
    expired_in = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        is_new = self._state.adding
        if is_new and self.status == 'active' and self.paid_at is None:
            from django.utils import timezone
            from datetime import timedelta
            self.paid_at = timezone.now()
            if self.payment_method == 'weekly':
                self.expired_in = self.paid_at + timedelta(days=7)
            elif self.payment_method == 'monthly':
                self.expired_in = self.paid_at + timedelta(days=30)
        super().save(*args, **kwargs)