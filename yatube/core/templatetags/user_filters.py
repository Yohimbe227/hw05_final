from django import template

from posts.forms import PostForm

register = template.Library()


@register.filter
def addclass(field: PostForm.base_fields, css: str) -> str:
    return field.as_widget(
        attrs={
            "class": css,
        },
    )
