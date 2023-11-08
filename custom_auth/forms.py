from typing import Any
from django import forms
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.contrib.auth.forms import UserChangeForm
from .models import CustomUser as User


class UserAdminCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""

    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "name",
            "books",
            "is_staff",
            "groups",
        )

    def check_fields(self):
        issued_books = User.objects.all().values_list("books", flat=True)
        curr_books = set()
        for i in issued_books:
            for a in i:
                curr_books.add(a)

        for book in self.cleaned_data["books"]:
            if (book or 0) < 1:
                raise ValueError("Enter valid book number.")
            if book in curr_books:
                raise ValueError(f"Book {book} is already issued.")

    def check_fields(self):
        issued_books = User.objects.exclude(
            username=self.cleaned_data["username"]
        ).values_list("books", flat=True)
        curr_books = set()
        for i in issued_books:
            for a in i:
                curr_books.add(a)

        for book in self.cleaned_data["books"]:
            if (book or 0) < 1:
                raise forms.ValidationError("Enter valid book number.")
            if book in curr_books:
                raise forms.ValidationError(f"Book {book} is already issued.")

    def clean_books(self):
        books = self.cleaned_data["books"]
        self.check_fields()
        return books

    def save(self, commit=True):
        user = super(UserAdminCreationForm, self).save(commit=False)
        password = self.cleaned_data["password"]  # Get the password from the form
        name = self.cleaned_data["name"]  # Get the password from the form
        user.set_password(password)
        user.name = name
        user.is_staff = True
        user.is_dealer = True
        if commit:
            user.save()
        return user


class UserAdminChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    password hash display field.
    """

    password = ReadOnlyPasswordHashField(
        label=("Password"),
        help_text=(
            "Raw passwords are not stored, so there is no way to see this "
            "user’s password, but you can change the password using "
            '<a href="{}">this form</a>.'
        ),
    )

    class Meta:
        model = User
        fields = (
            "username",
            "password",
            "name",
            "amount_received",
            "books",
            "is_dealer",
            "is_staff",
            "is_superuser",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        password = self.fields.get("password")
        if password:
            password.help_text = password.help_text.format(
                f"../../{self.instance.pk}/password/"
            )

    def check_fields(self):
        issued_books = User.objects.exclude(
            username=self.cleaned_data["username"]
        ).values_list("books", flat=True)
        curr_books = set()
        for i in issued_books:
            for a in i:
                curr_books.add(a)

        for book in self.cleaned_data["books"]:
            if (book or 0) < 1:
                raise forms.ValidationError("Enter valid book number.")
            if book in curr_books:
                raise forms.ValidationError(f"Book {book} is already issued.")

    def clean_books(self):
        books = self.cleaned_data["books"]
        self.check_fields()
        return books
