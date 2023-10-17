from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    is_dealer = models.BooleanField(default=False)
    name = models.CharField(max_length=150, default="")
