from http import HTTPStatus
from typing import TypeVar

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model, Q, QuerySet
from dmr import APIError, Body, Controller, Path, Query, ResponseSpec, modify
from dmr.errors import ErrorModel, ErrorType
from dmr.plugins.pydantic import PydanticSerializer
from pydantic import TypeAdapter

from .models import Author, Book, User
from .schemas.general import (
    AuthorCreateSchema,
    AuthorDetailSchema,
    AuthorSchema,
    AuthorUpdateSchema,
    BookCreateSchema,
    BookDetailSchema,
    BookSchema,
    BookUpdateSchema,
    UserCreateSchema,
    UserDetailSchema,
    UserSchema,
)
from .schemas.requests import (
    AuthorDetailPathParams,
    AuthorListQueryParams,
    BookDetailPathParams,
    BookListQueryParams,
    UserDetailPathParams,
    UserListQueryParams,
)

_ModelT = TypeVar("_ModelT", bound=Model)


class BaseController(Controller[PydanticSerializer]):
    pass


class DetailController(BaseController):
    responses = (ResponseSpec(ErrorModel, status_code=HTTPStatus.NOT_FOUND),)

    def get_object(self, queryset: QuerySet[_ModelT], pk: int) -> _ModelT:

        try:
            return queryset.get(pk=pk)
        except ObjectDoesNotExist:
            raise APIError(
                self.format_error(
                    f"{queryset.model._meta.verbose_name} {pk} was not found",
                    error_type=ErrorType.not_found,
                ),
                status_code=HTTPStatus.NOT_FOUND,
            ) from None


class UserListController(BaseController):
    @modify(
        summary="List users",
        description="Retrieve a list of users with optional pagination.",
        tags=["Users"],
    )
    def get(self, parsed_query: Query[UserListQueryParams]) -> list[UserSchema]:

        user_list = User.objects.all()[
            parsed_query.offset : parsed_query.offset + parsed_query.limit
        ]
        adapter = TypeAdapter(list[UserSchema])

        validated_users = adapter.validate_python(user_list)

        return validated_users

    @modify(
        summary="Create a new user",
        description="Create a new user with the provided details.",
        tags=["Users"],
    )
    def post(self, parsed_body: Body[UserCreateSchema]) -> UserSchema:
        user = parsed_body.save()
        return UserSchema.model_validate(user)


class UserDetailController(DetailController):
    @modify(
        summary="Get user details",
        description="Retrieve the details of a specific user by ID.",
        tags=["Users"],
    )
    def get(
        self,
        parsed_path: Path[UserDetailPathParams],
    ) -> UserDetailSchema:
        user = self.get_object(User.objects.all(), parsed_path.id)
        return UserDetailSchema.model_validate(user)


class AuthorListController(BaseController):
    @modify(
        summary="List authors",
        description="Retrieve a list of authors with optional pagination and search.",
        tags=["Authors"],
    )
    def get(self, parsed_query: Query[AuthorListQueryParams]) -> list[AuthorSchema]:

        authors = Author.objects.all()
        if parsed_query.search:
            authors = authors.filter(
                Q(first_name__icontains=parsed_query.search)
                | Q(last_name__icontains=parsed_query.search)
            )

        author_list = authors[
            parsed_query.offset : parsed_query.offset + parsed_query.limit
        ]

        return [AuthorSchema.model_validate(author) for author in author_list]

    @modify(
        summary="Create a new author",
        description="Create a new author with the provided details.",
        tags=["Authors"],
        status_code=HTTPStatus.CREATED,
    )
    def post(self, parsed_body: Body[AuthorCreateSchema]) -> AuthorSchema:
        author = parsed_body.save()
        return AuthorSchema.model_validate(author)


class AuthorDetailController(DetailController):
    @modify(
        summary="Get author details",
        description="Retrieve the details of a specific author, including their books.",
        tags=["Authors"],
    )
    def get(
        self,
        parsed_path: Path[AuthorDetailPathParams],
    ) -> AuthorDetailSchema:
        author = self.get_object(
            Author.objects.prefetch_related("book_set"),
            parsed_path.id,
        )
        return AuthorDetailSchema.model_validate(author)

    @modify(
        summary="Update an author",
        description="Update the given fields of a specific author by ID.",
        tags=["Authors"],
    )
    def patch(
        self,
        parsed_path: Path[AuthorDetailPathParams],
        parsed_body: Body[AuthorUpdateSchema],
    ) -> AuthorSchema:
        author = self.get_object(Author.objects.all(), parsed_path.id)
        return AuthorSchema.model_validate(parsed_body.save(author, partial=True))


class BookListController(BaseController):
    @modify(
        summary="List books",
        description="Retrieve a list of books with optional pagination and filters.",
        tags=["Books"],
    )
    def get(self, parsed_query: Query[BookListQueryParams]) -> list[BookSchema]:

        print(f"{parsed_query=}")
        books = Book.objects.select_related("author")
        if parsed_query.author_id:
            books = books.filter(author_id=parsed_query.author_id)
        if parsed_query.search:
            books = books.filter(title__icontains=parsed_query.search)

        book_list = books[
            parsed_query.offset : parsed_query.offset + parsed_query.limit
        ]
        adapter = TypeAdapter(list[BookSchema])

        validated_books = adapter.validate_python(book_list)

        return validated_books

    @modify(
        summary="Create a new book",
        description="Create a new book with the provided details.",
        tags=["Books"],
        status_code=HTTPStatus.CREATED,
    )
    def post(self, parsed_body: Body[BookCreateSchema]) -> BookSchema:
        book = parsed_body.save()
        return BookSchema.model_validate(book)


class BookDetailController(DetailController):
    @modify(
        summary="Get book details",
        description="Retrieve the details of a specific book, including its reviews.",
        tags=["Books"],
    )
    def get(
        self,
        parsed_path: Path[BookDetailPathParams],
    ) -> BookDetailSchema:
        book = self.get_object(
            Book.objects.select_related("author").prefetch_related("review_set__user"),
            parsed_path.id,
        )
        return BookDetailSchema.model_validate(book)

    @modify(
        summary="Update a book",
        description="Update the given fields of a specific book by ID.",
        tags=["Books"],
    )
    def patch(
        self,
        parsed_path: Path[BookDetailPathParams],
        parsed_body: Body[BookUpdateSchema],
    ) -> BookSchema:
        book = self.get_object(Book.objects.all(), parsed_path.id)
        return BookSchema.model_validate(parsed_body.save(book, partial=True))
