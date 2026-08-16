# dmr-with-django-modern-schemas

A library API built with [Django Modern REST](https://pypi.org/project/django-modern-rest/)
and [Django Modern Schemas](https://pypi.org/project/django-modern-schemas/).

The goal of the project is to show, over a real domain of authors, books and
reviews, how `ModelSchema` derives Pydantic schemas from Django models:
fields computed by the model itself, relation traversal, nesting, partial write
schemas and persistence through `.save()`.

## Stack

| Piece | What for |
| --- | --- |
| Django 6.1 | ORM, migrations, admin |
| django-modern-rest | controllers, routing, request/response validation, OpenAPI |
| django-modern-schemas | `ModelSchema`, `Source`, `MethodSource` |
| Pydantic | serializer on the DMR side |
| uv | dependency management |

## Getting started

```bash
make install     # uv sync
make migrate     # creates the sqlite database
make load        # loads the sample catalog
make run         # http://localhost:8000
```

If you want to start from scratch at any point: `make reset` (drops the
database, migrates it and reloads the fixture).

### API documentation

| URL | What it is |
| --- | --- |
| `http://localhost:8000/api/info/docs` | Interactive reference (Scalar) |
| `http://localhost:8000/api/docs/openapi.json` | OpenAPI 3.2 spec |
| `http://localhost:8000/admin/` | Django admin |

### Credentials

The fixture includes an **`admin` / `admin123`** superuser. It is a development
credential, meant only for this demo. `make superuser` creates that same user if
you start from a database that does not come from the fixture.

## Endpoints

| Method | Path | Input schema | Output schema |
| --- | --- | --- | --- |
| `GET` | `/api/v1/authors` | `AuthorListQueryParams` | `list[AuthorSchema]` |
| `POST` | `/api/v1/authors` | `AuthorCreateSchema` | `AuthorSchema` (201) |
| `GET` | `/api/v1/authors/{id}` | `AuthorDetailPathParams` | `AuthorDetailSchema` |
| `PATCH` | `/api/v1/authors/{id}` | `AuthorUpdateSchema` | `AuthorSchema` |
| `GET` | `/api/v1/books` | `BookListQueryParams` | `list[BookSchema]` |
| `POST` | `/api/v1/books` | `BookCreateSchema` | `BookSchema` (201) |
| `GET` | `/api/v1/books/{id}` | `BookDetailPathParams` | `BookDetailSchema` |
| `PATCH` | `/api/v1/books/{id}` | `BookUpdateSchema` | `BookSchema` |
| `GET` | `/api/v1/users` | `UserListQueryParams` | `list[UserSchema]` |
| `POST` | `/api/v1/users` | `UserCreateSchema` | `UserSchema` |
| `GET` | `/api/v1/users/{id}` | `UserDetailPathParams` | `UserDetailSchema` |

Detail routes respond `404` with the DMR error format when the record does not
exist.

## What each schema demonstrates

They all live in [`src/app/schemas/general.py`](src/app/schemas/general.py).

| Schema | Capability |
| --- | --- |
| `AuthorSchema` | `MethodSource` — the value is computed by a model method (`full_name`, `books_count`) |
| `BookSchema` | flat FK as an id, plus the author name resolved by `MethodSource` |
| `ReviewSchema` | `Source("user.username")` — traversal through a dotted path into the related model |
| `AuthorDetailSchema` | `Source("book_set")` — reverse FK resolved as a collection |
| `BookDetailSchema` | nested schema (`author: AuthorSchema \| None`), reverse `Source` and aggregates through `MethodSource` |
| `AuthorCreateSchema` | `Config.fields` to pick the writable fields |
| `BookCreateSchema` | `Config.exclude` as an alternative to `fields` |
| `AuthorUpdateSchema`, `BookUpdateSchema` | `Config.optional = "__all__"` for the partial `PATCH` |

Persistence comes from the schema itself: `parsed_body.save()` creates, and
`parsed_body.save(instance, partial=True)` updates only the fields that were
sent.

### Sample response

```bash
curl -s localhost:8000/api/v1/books/17 | jq
```

```json
{
  "id": 17,
  "title": "Pedro Páramo",
  "author": {
    "id": 6,
    "first_name": "Juan",
    "last_name": "Rulfo",
    "full_name": "Juan Rulfo",
    "books_count": 2
  },
  "summary": "Juan Preciado va a Comala a buscar a su padre y encuentra un pueblo habitado solo por murmullos.",
  "isbn": "9780000006011",
  "reviews": [
    { "id": 87, "rating": 5, "comment": "", "reviewer": "mjimenez" }
  ],
  "reviews_count": 9,
  "average_rating": 4.222222222222222
}
```

### A detail of the contract

In the body the foreign key travels under the **model field name**, not under
its `attname`:

```json
POST /api/v1/books
{"title": "El informe de Brodie", "author": 2, "summary": "...", "isbn": "9789999999991"}
```

`django-modern-schemas` sets `alias="author_id"` on the field, but validation
goes through `DjangoGetter` (`from_attributes` mode) and there Pydantic looks up
by field name, so the alias never applies — the generated OpenAPI documents
`author`, which is what is actually accepted. If you send `author_id` it is
silently ignored and the book is created without an author. To make a typo like
that fail instead of passing unnoticed, add `extra = "forbid"` to the `Config`
of the write schemas.

## Sample data

The fixture [`src/app/fixtures/library.json`](src/app/fixtures/library.json)
ships 842 records with real bibliographic data:

| Model | Records |
| --- | --- |
| `Author` | 38 |
| `Book` | 96 |
| `User` | 41 (40 readers + the superuser) |
| `Review` | 432 |
| `BookInstance` | 235 |

Authors, dates and titles are real. The ISBNs are synthetic but satisfy the
ISBN-13 check digit, and the reviews were generated with a fixed seed so the set
is reproducible.

After touching the database, `make dump` regenerates the fixture.

## Structure

```
src/
├── app/
│   ├── controllers.py           # DMR controllers
│   ├── models.py                # Author, Book, Review, BookInstance, User
│   ├── urls.py                  # one Router per resource
│   ├── fixtures/library.json    # sample catalog
│   └── schemas/
│       ├── general.py           # read and write ModelSchemas
│       ├── requests.py          # path and query params
│       └── responses.py
└── config/
    ├── openapi.py               # OpenAPIConfig
    ├── settings.py
    └── urls.py                  # mounts the router under /api/v1
```

## Commands

| Command | What it does |
| --- | --- |
| `make install` | `uv sync` |
| `make run` | Starts the server on port 8000 |
| `make check` | Django system checks |
| `make test` | Runs the test suite |
| `make shell` | Django shell |
| `make migrations` | Generates migrations |
| `make migrate` | Applies migrations |
| `make superuser` | Creates the `admin` / `admin123` superuser |
| `make load` | Loads the catalog from the fixture |
| `make dump` | Regenerates the fixture from the current database |
| `make reset` | Drops the database, migrates it and reloads the fixture |
