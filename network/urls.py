
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("create/",views.tweetSubmit, name="create" ),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register"),
    path("all/", views.allTweets, name="all"),
    path("user/<username>", views.userProfile, name="profile"),
    path("following/", views.following, name="following"),
    path("edit/<tweetId>", views.edit, name="tweetEdit"),
    path("like/<tweetId>", views.like, name="tweetLike"),
]
