from typing import Annotated

from django_modern_schemas import MethodSource, ModelSchema

from .models import User


class UserSchema(ModelSchema[User]):
    full_name: Annotated[str, MethodSource("get_full_name")]

    class Config:
        model = User
        model_fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
        )
