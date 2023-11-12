from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django_jsonform.models.fields import JSONField


USER_BOOKS = {
    "type": "array",
    "items": {
        "type": "number",
        "minimum": "1",
    },
}


class CustomUser(AbstractUser):
    is_dealer = models.BooleanField(default=False)
    name = models.CharField(max_length=150, default="")
    books = JSONField(schema=USER_BOOKS, default=[])
    total_amount = models.IntegerField(default=0)

    def __str__(self) -> str:
        return f"{self.username} - {self.name}"


class UserDeposit(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    amount = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    date = models.DateField(default=timezone.now)

    def __str__(self) -> str:
        return f"{self.user} - {self.amount} - {self.date}"
