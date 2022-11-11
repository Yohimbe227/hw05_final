from http import HTTPStatus
from http.client import HTTPResponse
from typing import Any

from django.http import HttpRequest
from django.shortcuts import render


def page_not_found(request: HttpRequest, *args: Any) -> HTTPResponse:
    return render(
        request,
        'core/404.html',
        {
            'path': request.path,
        },
        HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request: HttpRequest, *args: Any) -> HTTPResponse:
    return render(request, 'core/403csrf.html')


def server_failure(request: HttpRequest) -> HTTPResponse:
    return render(request, 'core/error500.html')
