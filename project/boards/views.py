from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic


# Create your views here.
@login_required
def home(request):
    boards = Board.objects.all()
    context = {'boards': boards}

    return render(request, 'home.html', context)


@login_required
def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    context = {'board': board}

    return render(request, 'topics.html', context)


@login_required
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)

    if request.method == 'POST':
        form = NewTopicForm(request.POST)

        if form.is_valid():
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save()

            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )

            return redirect('topic_posts', pk=board.pk, topic_pk=topic.pk)
    else:
        form = NewTopicForm()

    context = {'board': board, 'form': form}

    return render(request, 'new_topic.html', context)


@login_required
def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk, board__pk=pk)

    context = {'topic': topic}
    return render(request, 'topic_posts.html', context)


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
