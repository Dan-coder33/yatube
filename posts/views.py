from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.views.decorators.cache import cache_page

from .forms import NewPostForm, CommentForm
from .models import Post, Group, Follow


@cache_page(20, key_prefix="index_page")
def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "index.html",
        {"page": page, "paginator": paginator}
    )


@login_required
def new_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")

        return render(request, "new_post.html", {"form": form, "edit": False})

    form = NewPostForm()
    return render(request, "new_post.html", {"form": form, "edit": False})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    post_list = Post.objects.filter(group=group).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    return render(
        request,
        "group.html",
        {"page": page, "paginator": paginator, "group": group}
    )


def profile(request, username):
    user = get_object_or_404(User, username=username)
    post_list = user.posts.order_by("-pub_date").all()
    count = post_list.count()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    self = False
    if request.user == user:
        self = True

    following = False
    if not request.user.is_anonymous:
        if Follow.objects.filter(
            user=User.objects.get(username=request.user),
            author=User.objects.get(username=username)
        ).count() != 0:
            following = True

    return render(
        request,
        "profile.html",
        {
            "username": username,
            "page": page,
            "paginator": paginator,
            "count": count,
            "author": user,
            "following": following,
            "self": self,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    post_list = post.author.posts.all()
    count = post_list.count()
    form = CommentForm(instance=None)
    items = post.comments.order_by("-created").all()

    self = False
    if request.user == post.author:
        self = True

    following = False
    if not request.user.is_anonymous:
        if Follow.objects.filter(
                user=User.objects.get(username=request.user.username),
                author=User.objects.get(username=username)
        ).count() != 0:
            following = True

    return render(
        request,
        "post.html",
        {
            "username": username,
            "post_id": post_id,
            "post": post,
            "count": count,
            "author": post.author,
            "form": form,
            "items": items,
            "following": following,
            "self": self,
        }
    )


def post_edit(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)

    if post.author != request.user:
        return redirect("post", username, post_id)

    form = NewPostForm(
        data=request.POST or None,
        files=request.FILES or None,
        instance=post,
    )
    if form.is_valid():
        post.save()
        return redirect("post", username, post_id)

    return render(
        request,
        "new_post.html",
        {"form": form, "edit": True, "post": post}
    )


@login_required
def add_comment(request, username, post_id):
    post = get_object_or_404(Post, pk=post_id, author__username=username)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.post = post
        comment.author = request.user
        comment.save()
    return redirect("post", username=username, post_id=post_id)


@login_required
def follow_index(request):
    post_list = Post.objects.filter(
        author__following__in=Follow.objects.filter(user=request.user)
    ).order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)

    return render(
        request,
        "follow.html",
        {"page": page, "paginator": paginator}
    )


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    if (
            request.user != author
            and Follow.objects.filter(
                user=User.objects.get(username=request.user),
                author=User.objects.get(username=username)
            ).count() == 0
    ):
        Follow.objects.create(author=author, user=request.user)
    return redirect("profile", username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    Follow.objects.filter(
        user=request.user,
        author=author,
    ).delete()
    return redirect("profile", username=username)


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
