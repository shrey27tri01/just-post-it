from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.urls import reverse
from django.core.paginator import EmptyPage, InvalidPage, PageNotAnInteger, Paginator

from .models import User, Tweet, Profile

from .models import User
from django.http.response import Http404
import json

def index(request):
    if request.user.is_authenticated:
        allTweets = Tweet.objects.filter(user=request.user).all().order_by('-timestamp')
        tweetPaginator = Paginator(allTweets, 10)
        page = request.GET.get('page')
        try:
            tweets = tweetPaginator.page(page)
        except PageNotAnInteger:
            tweets = tweetPaginator.page(1)
        except EmptyPage:
            tweets = tweetPaginator.page(tweetPaginator.num_pages)
        context = {
            "allTweets": allTweets,
            "page": tweets
        }
        return render(request, "network/index.html", context)
    return render(request, "network/index.html")

def tweetSubmit(request):
    if request.method == 'POST':
        content = request.POST.get("tweet_content")
        # print(content)
        # print(request.user.username)
        username = request.user.username
        newTweet = Tweet(user=User.objects.filter(username=username).first(), content=content)
        newTweet.save()
        return HttpResponseRedirect(reverse("index"))
    return render(request, "network/index.html")

def allTweets(request):
    allTweets = Tweet.objects.all().order_by('-timestamp')
    tweetPaginator = Paginator(allTweets, 10)
    page = request.GET.get('page')
    try:
        tweets = tweetPaginator.page(page)
    except PageNotAnInteger:
        tweets = tweetPaginator.page(1)
    except EmptyPage:
        tweets = tweetPaginator.page(tweetPaginator.num_pages)
    context = {
        "allTweets": allTweets,
        "page": tweets,
        "currentuser": User.objects.filter(username=request.user.username).first()
    }
    return render(request, "network/alltweets.html", context)

def following(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse("login"))
    currentUserName = request.user.username
    profilesFollowing = User.objects.filter(username=currentUserName).first().following.all()
    # print(profilesFollowing)
    usersFollowing = []
    for profile in profilesFollowing:
        usersFollowing.append(profile.user)
    # print(usersFollowing)
    feed = []
    for user in usersFollowing:
        for tweet in user.tweets.all():
            feed.append(tweet)
    # print(feed)
    feed.reverse()
    # print(feed)
    tweetPaginator = Paginator(feed, 10)
    page = request.GET.get('page')
    try:
        tweets = tweetPaginator.page(page)
    except PageNotAnInteger:
        tweets = tweetPaginator.page(1)
    except EmptyPage:
        tweets = tweetPaginator.page(tweetPaginator.num_pages)
    context = {
        "tweets": feed,
        "page": tweets,
        "currentuser": User.objects.filter(username=request.user.username).first()
    }
    return render(request, "network/following.html", context)


# def userProfileRandom(request, username):
#     user = User.objects.filter(username=request.user.username).first()
#     viewedUser = User.objects.filter(username=username).first()
#     viewedUserTweets = Tweet.objects.filter(user=viewedUser).order_by('-timestamp')
#     viewedUserfollowers = viewedUser.profile.followers.all()
#     viewedUserFollowerNames = []
#     for user in viewedUserfollowers:
#         viewedUserFollowerNames.append(user.username)
#     viewedUserfollowerCount = viewedUserfollowers.count()
#     viewedUserFollowing = viewedUser.following.all()
#     # print(viewedUserFollowerNames)
#     # print(request.user.username)
#     viewedUserFollowingCount = viewedUser.following.all().count()
#     # print(viewedUser.username, request.user.username)
#     if request.user.username in viewedUserFollowerNames:
#         isFollowing = True
#     else:
#         isFollowing = False
#     if user == viewedUser:
#         data = {
#             "response": "Permission Denied"
#         }
#         return JsonResponse(data, status=403)
#     if request.method == "POST":
#         # print(f"Follow buton is clicked by {request.user.username} to follow {username}")
#         if isFollowing == True:
#             viewedUser.profile.followers.remove(request.user)
#             isFollowing = False
#             viewedUserfollowerCount -= 1
#         else:
#             viewedUser.profile.followers.add(request.user)
#             isFollowing = True
#             viewedUserfollowerCount += 1
#     context = {
#         "usertweets": viewedUserTweets,
#         "username": username,
#         "followerCount": viewedUserfollowerCount,
#         "followingCount": viewedUserFollowingCount,
#         "isFollowing": isFollowing
#     }
#     return render(request, "network/profile.html", context)

def edit(request, tweetId):
    user = User.objects.filter(username=request.user.username).first()
    tweetOwner = Tweet.objects.filter(id=tweetId).first().user
    tweet = Tweet.objects.filter(id=tweetId).first()
    # print(tweet.content)
    if user != tweetOwner:
        data = {
            "response": "Unauthorized user"
        }
        return JsonResponse(data, status=401)
    if request.method == 'POST' and request.is_ajax():
        newContent = json.loads(request.body.decode('utf-8')).get("content")
        try:
            tweet.content = newContent
            tweet.save()
            data = {
                "response": "success"
            }
            return JsonResponse(data, status=200)
        except LookupError as e:
            data = {
                "response": e
            }
            return JsonResponse(data, status=400)
    data = {
        "response": "Method not allowed"
    }
    return JsonResponse(data, status=405)

def like(request, tweetId):
    user = User.objects.filter(username=request.user.username).first()
    tweet = Tweet.objects.filter(id=tweetId).first()
    tweetOwner = Tweet.objects.filter(id=tweetId).first().user
    if user == tweetOwner:
        data = {
            "response": "Permission Denied"
        }
        return JsonResponse(data, status=403)
    if request.method == 'POST' and request.is_ajax():
        if user in tweet.likes.all():
            try:
                tweet.likes.remove(user)
                tweet.save()
                data = {
                    "response": "success",
                    "action": "unliked",
                    "likeCount": tweet.likes.all().count()
                }
                return JsonResponse(data, status=200)
            except LookupError as e:
                data = {
                    "response": e
                }
                return JsonResponse(data, status=400)
        elif user not in tweet.likes.all():
            try:
                tweet.likes.add(user)
                tweet.save()
                data = {
                    "response": "success",
                    "action": "liked",
                    "likeCount": tweet.likes.all().count()
                }
                return JsonResponse(data, status=200)
            except LookupError as e:
                data = {
                    "response": e
                }
                return JsonResponse({"response": "An error occurred"}, status=400)
    data = {
        "response": "Method not allowed"
    }
    return JsonResponse(data, status=405)

def userProfile(request, username):
    currentUser = User.objects.filter(username=request.user.username).first()
    viewedUser = User.objects.filter(username=username).first()
    viewedUserFollowers = viewedUser.profile.followers.all()
    viewedUserFollowersCount = viewedUser.profile.followers.count()
    viewedUserFollowingCount = viewedUser.following.count()
    viewedUserTweets = viewedUser.tweets.all()
    if currentUser in viewedUserFollowers:
        isFollowing = True
    else:
        isFollowing = False
    if request.method == 'POST' and currentUser == viewedUser:
        data = {
            "response": "Permission Denied"
        }
        return JsonResponse(data, status=403)
    if request.method == 'POST' and request.is_ajax():
        if currentUser in viewedUserFollowers:
            try:
                viewedUser.profile.followers.remove(currentUser)
                viewedUser.save()
                data = {
                    "response": "success",
                    "followerCount": viewedUser.profile.followers.count(),
                    "action": "unfollowed"
                }
                return JsonResponse(data, status=200)
            except Exception as e:
                data = {
                    "response": e
                }
                return JsonResponse(data, status=400)
        elif currentUser not in viewedUserFollowers:
            try:
                viewedUser.profile.followers.add(currentUser)
                viewedUser.save()
                data = {
                    "response": "success",
                    "followerCount": viewedUser.profile.followers.count(),
                    "action": "followed"
                }
                return JsonResponse(data, status=200)
            except Exception as e:
                data = {
                    "response": e
                }
                return JsonResponse(data, status=400)
    context = {
        "usertweets": viewedUserTweets,
        "username": username,
        "followerCount": viewedUserFollowersCount,
        "followingCount": viewedUserFollowingCount,
        "isFollowing": isFollowing
    }
    return render(request, "network/profile.html", context)

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
        # userProfile = Profile.objects.create(user=user)
        # userProfile.save()
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "network/register.html")
