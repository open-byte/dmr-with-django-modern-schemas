from dmr.openapi import OpenAPIConfig
from dmr.openapi.objects import Server

openapi_config = OpenAPIConfig(
    title="Demo API - Django Modern REST with Django Modern Schemas",
    summary="A demo API built with Django Modern REST and Django Modern Schemas",
    version="1.0.0",
    openapi_version="3.2.0",
    servers=[
        Server(
            url="http://localhost:8000",
            description="Local development server",
        ),
    ],
)
