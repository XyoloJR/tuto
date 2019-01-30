from django.shortcuts import render
from django.http import HttpResponse
from boards.models import Board
# Create your views here.


def home(request):
    response_html = '<ul>'

    for board in Board.objects.all():
        response_html += '<li>' + board.name + '<br>'
        response_html += board.description + ' topics nb : ' + str(len(board.topics.all())) + '</li>'

    response_html += '</ul>'

    return HttpResponse(response_html)
