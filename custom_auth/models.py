from django.db import models
from django.contrib.auth.models import AbstractUser

from django_jsonform.models.fields import JSONField


USER_BOOKS = {
    "type": "array",
    "items": {
        "type": "number",
        "minimum": "1",
    },
    "minItems": 1,
}


class CustomUser(AbstractUser):
    is_dealer = models.BooleanField(default=False)
    name = models.CharField(max_length=150, default="")
    books = JSONField(schema=USER_BOOKS, default=[])

    def __str__(self) -> str:
        return f"{self.username} - {self.name}"

    
