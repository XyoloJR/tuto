from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.http import Http404
from boards.models import Board, Topic, Post
# Create your views here.


def home(request):
    boards = Board.objects.all()
    context = {'boards': boards}

    return render(request, 'home.html', context)


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    topics = board.topics.all()
    context = {'board': board, 'topics': topics}

    return render(request, 'topics.html', context)


def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)

    context = {'board': board}

    if request.method == 'POST':
        subject = request.POST['subject']
        message = request.POST['message']

        user = User.objects.first()  # update with current user

        topic = Topic.objects.create(
            subject=subject,
            board=board,
            starter=user,
        )

        post = Post.objects.create(
            message=message,
            topic=topic,
            created_by=user,
        )

        return redirect('board_topics', pk=board.pk)  # redirect to topic messages page

    return render(request, 'new_topic.html', context)
