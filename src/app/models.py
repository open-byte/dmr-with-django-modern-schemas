from datetime import timezone

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser): ...


class Author(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField("Died", null=True, blank=True)

    def get_full_name(self) -> str:
        """
        Returns the full name of the author.
        """
        return f"{self.first_name} {self.last_name}"

    def get_quantity_of_books(self) -> int:
        """
        Returns the number of books written by the author.
        """
        return self.book_set.count()


class Book(models.Model):
    title = models.CharField(max_length=200)
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True)
    summary = models.TextField(
        max_length=1000, help_text="Enter a brief description of the book"
    )
    isbn = models.CharField(
        "ISBN", max_length=13, unique=True, help_text="13 Character ISBN number"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField(max_length=1000, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BookInstance(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    imprint = models.CharField(max_length=200)
    due_back = models.DateField(null=True, blank=True)
    borrower = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    LOAN_STATUS = (
        ("m", "Maintenance"),
        ("o", "On loan"),
        ("a", "Available"),
        ("r", "Reserved"),
    )

    status = models.CharField(
        max_length=1, choices=LOAN_STATUS, blank=True, default="m"
    )

    def is_overdue(self) -> bool:
        """
        Returns True if the book is overdue, False otherwise.
        """
        return self.due_back and self.due_back < timezone.now().date()
