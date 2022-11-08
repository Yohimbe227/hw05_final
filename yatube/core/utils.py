from django.core.paginator import Page, Paginator


def paginate(request, post_list, objects_per_page) -> Page:
    return Paginator(post_list, objects_per_page).get_page(
        request.GET.get('page')
    )


def cut_text(text, number_cuted_letters) -> str:
    return (
        text[:number_cuted_letters] + '…'
        if len(text) > number_cuted_letters
        else text
    )
