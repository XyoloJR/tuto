from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.http import Http404
from boards.models import Board
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

    return render(request, 'new_topic.html', context)
