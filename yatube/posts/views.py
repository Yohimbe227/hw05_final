from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


@cache_page(20, key_prefix='index_page')
def index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'posts/index.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.select_related(
                    'author',
                    'group',
                ),
                settings.OBJECTS_PER_PAGE,
            ),
        },
    )


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    return render(
        request,
        'posts/group_list.html',
        {
            'group': group,
            'page_obj': paginate(
                request,
                group.posts.select_related('group'),
                settings.OBJECTS_PER_PAGE,
            ),
        },
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    follows = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    return render(
        request,
        'posts/profile.html',
        {
            'author': author,
            'page_obj': paginate(
                request,
                author.posts.select_related('author'),
                settings.OBJECTS_PER_PAGE,
            ),
            'following': follows,
        },
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': CommentForm(request.POST or None),
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})
    form.instance.author = request.user
    form.save()
    return redirect('posts:profile', request.user)


@login_required
def post_edit(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    if post.author != request.user:
        return redirect('posts:post_detail', pk=post.pk)
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', pk=post.pk)
    return render(
        request,
        'posts/create_post.html',
        {
            'form': form,
            'is_edit': True,
        },
    )


@login_required
def add_comment(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    form = CommentForm(data=request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', pk=pk)


@login_required
def follow_index(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        'posts/follow.html',
        {
            'page_obj': paginate(
                request,
                Post.objects.filter(author__following__user=request.user),
                settings.OBJECTS_PER_PAGE,
            ),
        },
    )


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    if author != request.user:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', author)


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    get_object_or_404(
        Follow,
        user=request.user,
        author__username=username,
    ).delete()
    return redirect('posts:profile', request.user)
