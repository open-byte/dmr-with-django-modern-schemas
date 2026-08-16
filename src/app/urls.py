from dmr import Controller
from dmr.plugins.pydantic import PydanticSerializer


class BaseController(Controller[PydanticSerializer]):
    pass
