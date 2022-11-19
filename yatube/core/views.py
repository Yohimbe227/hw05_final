from http import HTTPStatus
from typing import Any

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render


def page_not_found(request: HttpRequest, exception) -> HttpResponse:
    del exception
    return render(
        request,
        "core/404.html",
        {
            "path": request.path,
        },
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request: HttpRequest, *args: Any) -> HttpResponse:
    return render(
        request,
        "core/403csrf.html",
        status=HTTPStatus.FORBIDDEN,
    )


def server_failure(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "core/500.html",
        status=HTTPStatus.INTERNAL_SERVER_ERROR,
    )
