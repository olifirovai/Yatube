from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import PostForm, CommentForm
from .models import Group, Post, User, Follow


@cache_page(20)
def index(request):
    post_list = Post.objects.order_by("-pub_date").all()
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    data = {"page": page, "paginator": paginator}
    return render(request, "index.html", data)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts_list = group.group_posts.order_by("-pub_date")
    paginator = Paginator(posts_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    data = {"group": group, "paginator": paginator, "page": page}
    return render(request, "group.html", data)


@login_required
def new_post(request):
    if request.method == "POST":
        form = PostForm(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("index")
    else:
        form = PostForm()
    return render(request, "posts/new_post.html", {"form": form})


def profile(request, username):
    author = get_object_or_404(User, username=username)
    posts = author.author_posts.filter(author=author).order_by("-pub_date")
    paginator = Paginator(posts, 10)
    posts_number = posts.count()
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    data = {"author": author, "paginator": paginator,
            "page": page, "posts_number": posts_number}
    return render(request, "posts/profile.html", data)


def post_view(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    posts_number = author.author_posts.filter(author=author).count()
    comments = post.post_comment.order_by("-created")
    data = {"author": author, "post": post, "posts_number": posts_number,
            "comments": comments, "form": CommentForm()}
    return render(request, "posts/post.html", data)


@login_required
def post_edit(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    if request.user == author:
        form = PostForm(request.POST or None, files=request.FILES or None,
                        instance=post)
        if request.method == "POST":
            if form.is_valid():
                post = form.save(commit=False)
                post.save()
                return redirect("post", username=post.author, post_id=post.id)
        else:
            form = PostForm(instance=post)
        data = {"form": form, "edit": True, "author": author, "post": post}
        return render(request, "posts/new_post.html", data)
    else:
        return redirect("post", username=author, post_id=post.id)


@login_required
def post_delete(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    if request.user == author:
        if request.method == "POST":
            form = PostForm(request.POST, instance=post)
            post.delete()
            return redirect("profile", username=post.author)
        else:
            form = PostForm(instance=post)
        data = {"form": form, "delete": True, "author": author, "post": post}
        return render(request, "posts/new_post.html", data)
    else:
        return redirect("post", username=author, post_id=post.id)


def page_not_found(request, exception):
    return render(request, "misc/404.html", {"path": request.path}, status=404)


def server_error(request):
    return render(request, "misc/500.html", status=500)


@login_required
def add_comment(request, username, post_id):
    author = get_object_or_404(User, username=username)
    post = get_object_or_404(author.author_posts, id=post_id)
    comments = post.post_comment.all()
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = post
            comment.save()
            return redirect("post", username=author, post_id=post.id)
    else:
        form = CommentForm()
    return render(request, "posts/comments.html",
                  {"form": form, "comments": comments, "post": post})


@login_required
def follow_index(request):
    author_list = Follow.objects.filter(user=request.user).all()
    # for num in range(author_list.count()):
    #     post_list = Post.objects.filter(
    #         author__exact=author_list[num].author).order_by("-pub_date")
    author_names_list = []
    for author_name in author_list:
        author_names_list.append(author_name.author)

    post_list = Post.objects.filter(
        author__in=author_names_list).order_by("-pub_date")
    # post_list += posts_following_author
    paginator = Paginator(post_list, 10)
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    data = {"page": page, "paginator": paginator}
    return render(request, "posts/follow.html", data)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if follow:
        return redirect("profile", username=author)
    else:
        if request.user != author:
            Follow.objects.create(user=request.user, author=author)
    return redirect("profile", username=author)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    follow = Follow.objects.filter(user=request.user, author=author).exists()
    if follow:
        Follow.objects.create(user=request.user, author=author).delete()
    return redirect("profile", username=author)
