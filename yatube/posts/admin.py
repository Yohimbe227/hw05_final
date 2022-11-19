from django.contrib import admin

from core.admin import BaseAdmin
from posts.models import Comment, Follow, Group, Post


@admin.register(Post)
class PostAdmin(BaseAdmin):
    list_display = ("pk", "text", "pub_date", "author", "group")
    list_editable = ("group",)
    search_fields = ("text",)
    list_filter = ("pub_date",)


@admin.register(Group)
class GroupAdmin(BaseAdmin):
    list_display = ("pk", "title", "slug", "description")
    list_editable = ("description",)
    search_fields = ("title",)
    list_filter = ("slug",)


@admin.register(Comment)
class Comment(BaseAdmin):
    list_display = (
        "pk",
        "text",
        "created",
    )
    list_editable = ("text",)
    search_fields = ("created",)
    list_filter = ("created",)


@admin.register(Follow)
class Comment(BaseAdmin):
    list_display = (
        "pk",
        "user",
        "author",
    )
    list_editable = ("user",)
    search_fields = (
        "user",
        "author",
    )
    list_filter = ("user",)
