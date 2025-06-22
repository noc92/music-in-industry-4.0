from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    jobinfo = models.CharField(max_length=255)
    jobexplain = models.TextField()

    def __str__(self):
        return self.user.username

# Create your models here.
