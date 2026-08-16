from typing import Annotated

from django.contrib.auth.models import Group
from django_modern_schemas import MethodSource, ModelSchema, Source

from ..models import Author, Book, Review, User


class GroupSchema(ModelSchema[Group]):
    class Config:
        model = Group
        fields = ("id", "name")


class UserSchema(ModelSchema[User]):
    full_name: Annotated[str, MethodSource("get_full_name")]

    class Config:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )


class UserDetailSchema(ModelSchema[User]):
    full_name: Annotated[str, MethodSource("get_full_name")]

    class Config:
        model = User
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "date_joined",
            "last_login",
            "is_active",
            "is_staff",
            "is_superuser",
        )


class UserCreateSchema(ModelSchema[User]):
    class Config:
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
        )


class AuthorSchema(ModelSchema[Author]):
    full_name: Annotated[str, MethodSource("get_full_name")]
    books_count: Annotated[int, MethodSource("get_quantity_of_books")]

    class Config:
        model = Author
        fields = (
            "id",
            "first_name",
            "last_name",
        )


class BookSchema(ModelSchema[Book]):
    author_name: Annotated[str | None, MethodSource("get_author_name")]

    class Config:
        model = Book
        fields = (
            "id",
            "title",
            "isbn",
            "author",
        )


class ReviewSchema(ModelSchema[Review]):
    reviewer: Annotated[str, Source("user.username")]

    class Config:
        model = Review
        fields = (
            "id",
            "rating",
            "comment",
            "created_at",
        )


class AuthorDetailSchema(ModelSchema[Author]):
    full_name: Annotated[str, MethodSource("get_full_name")]
    books_count: Annotated[int, MethodSource("get_quantity_of_books")]
    books: Annotated[list[BookSchema], Source("book_set")]

    class Config:
        model = Author
        fields = (
            "id",
            "first_name",
            "last_name",
            "date_of_birth",
            "date_of_death",
        )


class BookDetailSchema(ModelSchema[Book]):
    author: AuthorSchema | None
    reviews: Annotated[list[ReviewSchema], Source("review_set")]
    reviews_count: Annotated[int, MethodSource("get_quantity_of_reviews")]
    average_rating: Annotated[float | None, MethodSource("get_average_rating")]

    class Config:
        model = Book
        fields = (
            "id",
            "title",
            "summary",
            "isbn",
            "created_at",
            "updated_at",
        )


class AuthorCreateSchema(ModelSchema[Author]):
    class Config:
        model = Author
        fields = (
            "first_name",
            "last_name",
            "date_of_birth",
            "date_of_death",
        )


class AuthorUpdateSchema(ModelSchema[Author]):
    class Config:
        model = Author
        fields = (
            "first_name",
            "last_name",
            "date_of_birth",
            "date_of_death",
        )
        optional = "__all__"


class BookCreateSchema(ModelSchema[Book]):
    class Config:
        model = Book
        exclude = (
            "id",
            "created_at",
            "updated_at",
        )


class BookUpdateSchema(ModelSchema[Book]):
    class Config:
        model = Book
        exclude = (
            "id",
            "created_at",
            "updated_at",
        )
        optional = "__all__"
