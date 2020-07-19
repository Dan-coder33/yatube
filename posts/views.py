from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator

from .forms import NewPostForm
from .models import Post, Group


def index(request):
    # latest = Post.objects.order_by("-pub_date")[:11]
    # return render(request, "index.html", {"posts": latest})

    post_list = Post.objects.order_by('-pub_date').all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get('page')
    page = paginator.get_page(page_number)
    return render(
        request,
        'index.html',
        {'page': page, 'paginator': paginator}
    )


def new_post(request):
    if request.method == "POST":
        form = NewPostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")

        return render(request, "new_post.html", {"form": form})

    form = NewPostForm()
    return render(request, "new_post.html", {"form": form})


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)

    posts = Post.objects.filter(group=group).order_by("-pub_date")[:12]
    return render(request, "group.html", {"group": group, "posts": posts})
