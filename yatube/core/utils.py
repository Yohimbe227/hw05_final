from typing import List

from django.core.paginator import Page, Paginator
from django.http import HttpRequest

from yatube import settings


def paginate(
    request: HttpRequest, post_list: List, objects_per_page: int
) -> Page:
    return Paginator(post_list, objects_per_page).get_page(
        request.GET.get('page'),
    )


def cut_text(
    text: str, number_cuted_letters: int = settings.LETTERS_IN_TITLE
) -> str:
    return (
        text[:number_cuted_letters] + '…'
        if len(text) > number_cuted_letters
        else text
    )
