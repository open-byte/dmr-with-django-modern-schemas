"""
URL configuration for library project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import include
from django.urls import path as django_path
from dmr.openapi import build_schema
from dmr.openapi.views import OpenAPIJsonView, ScalarView
from dmr.routing import Router, path

from app.urls import router as app_router

from .openapi import openapi_config

router = Router(prefix="api/v1")
router.include(app_router, namespace="api", app_name="api")
api_schema = build_schema(router, config=openapi_config)

api_urlpatterns = [
    path(router.prefix, include((router.urls, "api"), namespace="api")),
    path("api/docs/openapi.json", OpenAPIJsonView.as_view(api_schema), name="openapi"),
    path("api/info/docs", ScalarView.as_view(api_schema), name="scalar"),
]


urlpatterns = [
    django_path("admin/", admin.site.urls),
] + api_urlpatterns
