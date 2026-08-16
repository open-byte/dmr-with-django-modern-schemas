from pydantic import BaseModel, Field


class UserDetailPathParams(BaseModel):
    id: int = Field(..., description="The ID of the user")


class UserListQueryParams(BaseModel):
    offset: int = Field(0, description="The offset for pagination")
    limit: int = Field(10, description="The limit for pagination")


class AuthorDetailPathParams(BaseModel):
    id: int = Field(..., description="The ID of the author")


class AuthorListQueryParams(BaseModel):
    offset: int = Field(0, description="The offset for pagination")
    limit: int = Field(10, description="The limit for pagination")
    search: str | None = Field(None, description="Filter authors by their name")


class BookDetailPathParams(BaseModel):
    id: int = Field(..., description="The ID of the book")


class BookListQueryParams(BaseModel):
    offset: int = Field(0, description="The offset for pagination")
    limit: int = Field(10, description="The limit for pagination")
    author_id: int | None = Field(None, description="Filter books by their author")
    search: str | None = Field(None, description="Filter books by their title")
