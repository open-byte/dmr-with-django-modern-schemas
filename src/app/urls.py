from dmr.routing import Router, path

from .controllers import (
    AuthorDetailController,
    AuthorListController,
    BookDetailController,
    BookListController,
    UserDetailController,
    UserListController,
)

users_router = Router(
    prefix="/users",
    tags=["Users"],
    urls=[
        path(
            "",
            UserListController.as_view(),
            name="user-list",
        ),
        path(
            "/<int:id>",
            UserDetailController.as_view(),
            name="user-detail",
        ),
    ],
)

authors_router = Router(
    prefix="/authors",
    tags=["Authors"],
    urls=[
        path(
            "",
            AuthorListController.as_view(),
            name="author-list",
        ),
        path(
            "/<int:id>",
            AuthorDetailController.as_view(),
            name="author-detail",
        ),
    ],
)

books_router = Router(
    prefix="/books",
    tags=["Books"],
    urls=[
        path(
            "",
            BookListController.as_view(),
            name="book-list",
        ),
        path(
            "/<int:id>",
            BookDetailController.as_view(),
            name="book-detail",
        ),
    ],
)

router = Router()
router.include(users_router, namespace="users", app_name="users")
router.include(authors_router, namespace="authors", app_name="authors")
router.include(books_router, namespace="books", app_name="books")
