from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .forms import NewPostForm
from .models import Post, Group


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
    return render(
        request,
        "profile.html",
        {
            "username": username,
            "page": page,
            "paginator": paginator,
            "count": count,
            "author": user,
        }
    )


def post_view(request, username, post_id):
    post = get_object_or_404(Post, author__username=username, id=post_id)
    post_list = post.author.posts.all()
    count = post_list.count()
    return render(
        request,
        "post.html",
        {
            "username": username,
            "post_id": post_id,
            "post": post,
            "count": count,
            "author": post.author,
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


def page_not_found(request, exception):
    return render(
        request,
        "misc/404.html",
        {"path": request.path},
        status=404
    )


def server_error(request):
    return render(request, "misc/500.html", status=500)
