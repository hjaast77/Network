from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import User, Post, Follow, Like
from django.core.paginator import Paginator


def index(request):

    allPosts = Post.objects.all()
    #Create list that holds post info & likes count
    posts = []
    for post in allPosts:
        likes = post.likes.count()
        posts.append((post, likes))

    paginator = Paginator(posts, 10) # Show 10 posts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/index.html", {'page_obj': page_obj})

def create(request):
    if request.method =="POST":
        postText = request.POST["postText"]
        user = request.user

        newPost = Post(
            postContent=postText,
            user=user
        )

        newPost.save()

        return HttpResponseRedirect(reverse(index))
    
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

def profile(request, user_id):

    profile_user = get_object_or_404(User, id=user_id)

    is_following = Follow.objects.filter(follower=request.user, followed_user=profile_user).exists()
    # Count the number of followers (users following the current user)
    followers_count = Follow.objects.filter(followed_user=profile_user).count()

    # Count the number of users followed by the current user
    following_count = Follow.objects.filter(follower=profile_user).count()

    userPosts = profile_user.author.all()
    posts = []
    for post in userPosts:
        likes = post.likes.count()
        posts.append((post, likes))

    paginator = Paginator(posts, 2) # Show 10 posts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    

    return render(request, "network/profile.html", {"page_obj":  page_obj, "profile_user": profile_user, "following": following_count, "followed": followers_count, "isFollowing": is_following})

def follow_user(request, user_id):
    userToFollow = get_object_or_404(User, id=user_id)
    if request.user != userToFollow:
        if not Follow.objects.filter(follower=request.user, followed_user=userToFollow).exists():
            Follow.objects.create(follower=request.user, followed_user=userToFollow)

    return redirect('profile', user_id=user_id)

def unfollow_user(request, user_id):
    userToUnfollow = get_object_or_404(User, id=user_id)

    if request.user != userToUnfollow:
        Follow.objects.filter(follower=request.user, followed_user=userToUnfollow).delete()

    return redirect('profile', user_id=user_id)

def following(request):
    #filter post of followed users

    following_users = Follow.objects.filter(follower=request.user).values_list('followed_user', flat=True)
    posts_from_following = Post.objects.filter(user__in=following_users).order_by('-created')
    
    posts = []
    for post in  posts_from_following:
        likes = post.likes.count()
        posts.append((post, likes))

    paginator = Paginator(posts, 2) # Show 10 posts per page.

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, "network/following.html", {"page_obj": page_obj})