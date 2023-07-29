from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import Paginator

from .models import User, Post, Follow


def index(request):
    all_posts = Post.objects.all().order_by("-timestamp")

    # reference to: https://docs.djangoproject.com/en/4.2/topics/pagination/
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('p')
    posts = paginator.get_page(page_number)

    
    return render(request, "network/index.html",{
        "posts": posts
    })


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "network/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "network/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "network/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "network/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")

def add_post(request):
    if request.method == "POST":
        post_content = request.POST["post-content"]
        user = request.user
        post = Post(content=post_content, author = user)
        post.save()
        return HttpResponseRedirect(reverse("index"))
    
def get_profile(request, id):
    user = User.objects.get(id=id)
    all_posts = Post.objects.filter(author = user).order_by("-timestamp")

    followings = Follow.objects.filter(user=user)
    followers  = Follow.objects.filter(followed = user)

    current_user = request.user
    is_following = followers.filter(user=User.objects.get(pk=current_user.id))
    is_following = bool(is_following)

    # reference to: https://docs.djangoproject.com/en/4.2/topics/pagination/
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('p')
    posts = paginator.get_page(page_number)

    
    return render(request, "network/profile.html",{
        "posts": posts,
        'username': user.username,
        'target_user_id': user.id,
        'followings': followings,
        'followers': followers,
        'is_following': is_following
    })

def follow(request):
    
    target_user = User.objects.get(id=request.POST.get('target-user-id'))
    current_user = request.user
    follow = Follow(user=current_user, followed=target_user)
    follow.save()
    return HttpResponseRedirect(reverse("profile", kwargs={"id": target_user.id}))

def unfollow(request):
    print(request.POST.get('target-user-id'))
    target_user = User.objects.get(id=request.POST.get('target-user-id'))
    current_user = request.user
    follow = Follow.objects.get(user=current_user, followed=target_user)
    follow.delete()
    return HttpResponseRedirect(reverse("profile", kwargs={"id": target_user.id}))