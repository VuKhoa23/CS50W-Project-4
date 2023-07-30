from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.http import JsonResponse
import json

from .models import User, Post, Follow, Like


def index(request):
    all_posts = Post.objects.all().order_by("-timestamp")

    # reference to: https://docs.djangoproject.com/en/4.2/topics/pagination/
    paginator = Paginator(all_posts, 10)
    page_number = request.GET.get('p')
    posts = paginator.get_page(page_number)

    likes = Like.objects.all()

    liked = []

    for like in likes:
        if like.user.id == request.user.id:
            liked.append(like.post.id)

    like = []
    for post in posts:
        like_on_post = Like.objects.filter(post=post).count()
        post.likes = like_on_post  
        post.save()
    

    return render(request, "network/index.html",{
        "posts": posts,
        "liked": liked
    })


def following(request):
    current_user = User.objects.get(id=request.user.id)
    followed_by_user = Follow.objects.filter(user=current_user)

    followed_post = []

    all_posts = Post.objects.all().order_by("-timestamp")

    for post in all_posts:
        for user in followed_by_user:
            if user.followed == post.author:
                followed_post.append(post)

    # reference to: https://docs.djangoproject.com/en/4.2/topics/pagination/
    paginator = Paginator(followed_post, 10)
    page_number = request.GET.get('p')
    posts = paginator.get_page(page_number)


    likes = Like.objects.all()

    liked = []

    for like in likes:
        if like.user.id == request.user.id:
            liked.append(like.post.id)

    like = []
    for post in posts:
        like_on_post = Like.objects.filter(post=post).count()
        post.likes = like_on_post  
        post.save()

    return render(request, "network/following.html",{
        "posts": posts,
        'liked': liked
    })

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


    likes = Like.objects.all()

    liked = []

    for like in likes:
        if like.user.id == request.user.id:
            liked.append(like.post.id)

    like = []
    for post in posts:
        like_on_post = Like.objects.filter(post=post).count()
        post.likes = like_on_post  
        post.save()

    
    return render(request, "network/profile.html",{
        "posts": posts,
        'username': user.username,
        'target_user_id': user.id,
        'followings': followings,
        'followers': followers,
        'is_following': is_following,
        'liked': liked
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


@csrf_exempt
def edit(request, id):
    if request.method == 'POST':
        body = json.loads(request.body)
        target_post = Post.objects.get(id=id)
        new_content = body['new_content']
        target_post.content = new_content
        target_post.save()
        return JsonResponse({
            'message': 'Success',
            'content': new_content,
        })   
    
def unlike(request, post_id):
    all_posts = Post.objects.all().order_by("-timestamp")
    
    target_post = Post.objects.get(id=post_id)
    user = User.objects.get(id=request.user.id)
    like_obj = Like.objects.filter(user=user,post=target_post)
    like_obj.delete()

    like_on_post = Like.objects.filter(post=target_post).count()
    likes = like_on_post
    return JsonResponse({
            'message': 'Unlike Success',
            'likes': likes,
        })  

def like(request, post_id):
    all_posts = Post.objects.all().order_by("-timestamp")

    target_post = Post.objects.get(id=post_id)
    user = User.objects.get(id=request.user.id)
    like_obj = Like(user=user, post=target_post)
    like_obj.save()

    like_on_post = Like.objects.filter(post=target_post).count()
    likes = like_on_post

    return JsonResponse({
            'message': 'Like Success',
            'likes': likes,
        })  

def get_like(request):
    likes = Like.objects.all()
    liked = []
    for like in likes:
        if like.user.id == request.user.id:
            liked.append(like.post.id)
    return JsonResponse({
            'liked': liked,
        })  