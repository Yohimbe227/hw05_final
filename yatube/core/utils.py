from typing import List

from django.conf import settings
from django.core.paginator import Page, Paginator
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    post_list: List,
    objects_per_page: int = settings.OBJECTS_PER_PAGE,
) -> Page:
    return Paginator(post_list, objects_per_page).get_page(
        request.GET.get("page"),
    )


def cut_text(
    text: str, number_cuted_letters: int = settings.NUMBER_CUTED_LETTERS
) -> str:
    return (
        text[:number_cuted_letters] + "…" if len(text) > number_cuted_letters else text
    )
