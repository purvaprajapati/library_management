from django.db import models
from accounts.models import UserProfile

class Member(models.Model):
    STATUS_CHOICES = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
    )

    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='member_profile')
    membership_id = models.CharField(max_length=50, unique=True)
    address = models.TextField(blank=True, null=True)
    join_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.user.name} ({self.membership_id})"
