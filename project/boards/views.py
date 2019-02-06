from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User

from .forms import NewTopicForm, PostForm
from .models import Board, Topic, Post


# Create your views here.
def home(request):
    boards = Board.objects.all()
    context = {'boards': boards}

    return render(request, 'home.html', context)


def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    context = {'board': board}

    return render(request, 'topics.html', context)


def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)

    user = User.objects.first()  # update with current user

    if request.method == 'POST':
        form = NewTopicForm(request.POST)

        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = user
            topic.save()

            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )

            return redirect('board_topics', pk=board.pk)  # redirect to topic messages page
    else:
        form = NewTopicForm()

    context = {'board': board, 'form': form}

    return render(request, 'new_topic.html', context)


def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk, board__pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            return redirect('board_topics', pk=pk)  # should redirect to topic posts
            # return redirect('topic_post', pk=pk, topic_pk=topic_pk)

    else:
        form = PostForm()

    context = {'topic': topic, 'form': form}

    return render(request, 'reply_topic.html', context)
