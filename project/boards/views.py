from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import NewTopicForm
from .models import Board, Post


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

            return redirect('board_topics', pk=board.pk)  # redirect to topic messages page
    else:
        form = NewTopicForm()

    context = {'board': board, 'form': form}

    return render(request, 'new_topic.html', context)
