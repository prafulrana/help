from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import render, redirect
from fix_it.forms import NewPost, NewComment
from fix_it.models import Post, Annotate
from geopy.geocoders import Nominatim


def front(request):
    posts_with_location = []

    for post in Post.objects.all():
        if post.location:
            posts_with_location.append(post)
    data = {
        'posts_with_location': posts_with_location,
        'user': request.user,
        'gkadillak': 'gkadillak'
    }

    return render(request, 'home.html', data)


def test_markers(request):
    data = {
        'posts': Post.objects.all()
    }

    return render(request, 'testmap.html', data)



def view_specific_post(request, post_id):
    data = {
        'post': Post.objects.filter(id=post_id)
    }

    return render(request, 'view_specific_post.html', data)


#@login_required
def new_post(request):
    data = {'new_post': NewPost()}
    if request.method == "POST":
        form = NewPost(request.POST, request.FILES)
        if form.is_valid():
            user = request.user

            # Store the latitude and longitude of location if given
            geolocator = Nominatim()
            location = geolocator.geocode(form.cleaned_data['location'])
            Post.objects.create(author=user, body=form.cleaned_data['body'], image=form.cleaned_data['image'],
                                location=form.cleaned_data['location'], latitude=location.latitude,
                                longitude=location.longitude, title=form.cleaned_data['title'])
    else:
        return render(request, 'new_post.html', data)

    # Change this to a 'Thanks for posting' screen
    return render(request, 'home.html', data)


def profile(request):
    data = {
        'posts': Post.objects.filter(author=request.user.id)
    }
    return render(request, 'profile.html', data)


def new_comment(request, post_id):
    # Attach the comment to the clicked post
    post = Post.objects.get(id=post_id)
    data = {
        'new_comment': NewComment(),
        'post': post
    }

    if request.method == "POST":
        form = NewComment(request.POST)
        if form.is_valid():
            Annotate.objects.create(post=post, comment=form.cleaned_data['comment'],
                                    author=request.user)
            return redirect('/')

    else:
        return render(request, 'new_comment.html', data)
    return redirect(request, 'new_comment.html', data)


def register(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = UserCreationForm()

    return render(request, 'registration/register.html', {
        'form': form
    })


def view_posts(request):
    data = {
        'posts': Post.objects.all()
    }

    return render(request, 'view_posts.html', data)


# def down_vote(request, comment_id):
#     comment = Annotate.objects.get(id=comment_id)
#     comment.thumb_up = False
#     comment.thumb_down = True
#     comment.down_votes += 1
#     comment.voted = True
#     comment.save()
#     # data = {
#     #     'comments': comments
#     # }
#     return redirect('/')


def up_vote(request, comment_id):
    liked_comment = Annotate.objects.get(id=comment_id)
    new_like = Like.objects.create(user_who_liked=request.user, liked_comment=liked_comment)
    new_like.save()

    return redirect('/')


def leaderboard(request):
    # Users with the most posts (i.e. the most helped)
    users_with_most_posts = User.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:5]
    users_with_most_comments = Post.objects.annotate(most_comms=Count('author')).order_by('-most_comms')[:5]
    most_comments = Annotate.objects.annotate(most_comms=Count('author')).order_by('-most_comms')[:5]

    data = {
        'users_with_most_posts': users_with_most_posts,
        'users_with_most_comments': users_with_most_comments,
        'most_comments': most_comments,


    }
    return render(request, 'leaderboard.html', data)



