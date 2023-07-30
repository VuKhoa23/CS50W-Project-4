
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),

    path("add-post", views.add_post, name="add-post"),
    path("profile/<int:id>", views.get_profile, name="profile"),
    path("follow", views.follow, name="follow"),
    path("unfollow", views.unfollow, name="unfollow"),
    path("following", views.following, name="following"),
    path("edit/<int:id>", views.edit, name="edit"),
    path("unlike/<int:post_id>", views.unlike, name="unlike"),
    path("like/<int:post_id>", views.like, name="like"),
    path("get-like", views.get_like, name="get-like"),
    path("profile/unlike/<int:post_id>", views.unlike, name="unlike"),
    path("profile/like/<int:post_id>", views.like, name="like"),
    path("profile/get-like", views.get_like, name="get-like"),
]
