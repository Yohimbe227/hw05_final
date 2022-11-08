from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from core.utils import paginate
from posts.forms import CommentForm, PostForm
from posts.models import Follow, Group, Post, User


@cache_page(20)
def index(request: HttpRequest) -> HttpResponse:
    posts = Post.objects.select_related(
        'author',
        'group',
    )
    paginator = paginate(request, posts, settings.OBJECTS_PER_PAGE)
    return render(request, 'posts/index.html', {'page_obj': paginator})


def group_posts(request: HttpRequest, slug: str) -> HttpResponse:
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('group')
    paginator = paginate(request, posts, settings.OBJECTS_PER_PAGE)
    return render(
        request,
        'posts/group_list.html',
        {'group': group, 'page_obj': paginator},
    )


def profile(request: HttpRequest, username: str) -> HttpResponse:
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('author')
    follows = False
    if request.user.is_authenticated:
        user = request.user
        follows = Follow.objects.filter(user=user, author=author).exists()
    paginator = paginate(request, posts, settings.OBJECTS_PER_PAGE)
    return render(
        request,
        'posts/profile.html',
        {'author': author, 'page_obj': paginator, 'following': follows},
    )


def post_detail(request: HttpRequest, pk: int) -> HttpResponse:
    post = get_object_or_404(Post, pk=pk)
    return render(
        request,
        'posts/post_detail.html',
        {
            'post': post,
            'form': CommentForm(request.POST or None),
            'comments': post.comments.all(),
        },
    )


@login_required
def post_create(request: HttpRequest) -> HttpResponse:
    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
    )
    if request.method != 'POST' or not form.is_valid():
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
    posts = Post.objects.filter(author__following__user=request.user)
    paginator = paginate(request, posts, settings.OBJECTS_PER_PAGE)
    return render(request, 'posts/follow.html', {'page_obj': paginator})


@login_required
def profile_follow(request: HttpRequest, username: str) -> HttpResponse:
    user = request.user
    author = User.objects.get(username=username)
    follows = Follow.objects.filter(author=author, user=user)
    if author != user and not follows.exists():
        Follow.objects.create(user=user, author=author)
    return redirect(
        'posts:profile',
        author,
    )


@login_required
def profile_unfollow(request: HttpRequest, username: str) -> HttpResponse:
    user = request.user
    author = get_object_or_404(User, username=username)
    follows = Follow.objects.filter(author=author, user=user)
    if follows.exists():
        follows.delete()
    return redirect('posts:profile', author)

