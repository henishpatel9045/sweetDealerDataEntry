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

    def check_fields(self):
        issued_books = CustomUser.objects.exclude(pk=self.pk).values_list(
            "books", flat=True
        )
        curr_books = set()
        for i in issued_books:
            for a in i:
                curr_books.add(a)

        for book in self.books:
            if (book or 0) < 1:
                raise ValueError("Enter valid book number.")
            if book in curr_books:
                raise ValueError(f"Book {book} is already issued.")

        print(curr_books)

    def save(self):
        self.check_fields()
        super().save()
