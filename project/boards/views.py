from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView, ListView
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from .forms import NewTopicForm, PostForm
from .models import Board, Post, Topic


# Create your views here.
@method_decorator(login_required, name='dispatch')
class HomeView(ListView):
    model = Board
    context_object_name = 'boards'
    template_name = 'home.html'


@login_required
def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk)
    queryset = board.topics.order_by('-last_update').annotate(replies=Count('posts') - 1)

    page = request.GET.get('page', 1)

    paginator = Paginator(queryset, 10)

    try:
        topics = paginator.page(page)
    except PageNotAnInteger:
        # fallback to the first page
        topics = paginator.page(1)
    except EmptyPage:
        # probably the user tried to add a page number
        # in the url, so we fallback to the last page
        topics = paginator.page(paginator.num_pages)

    context = {'board': board, 'topics': topics}

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
    topic.views += 1
    topic.save()

    context = {'topic': topic}
    return render(request, 'topic_posts.html', context)


@login_required
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, pk=topic_pk, board__pk=pk)

    if request.method == 'POST':
        form = PostForm(request.POST)

        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_update = post.created_at
            topic.save()

            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)

    else:
        form = PostForm()

    context = {'topic': topic, 'form': form}

    return render(request, 'reply_topic.html', context)


@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'update_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)

    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)
