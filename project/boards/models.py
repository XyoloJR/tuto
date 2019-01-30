from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Board(models.Model):
    name = models.CharField(max_length=30, unique=True, verbose_name='Domaine')
    description = models.CharField(max_length=100)


class Topic(models.Model):
    subject = models.CharField(max_length=255, verbose_name='Sujet')
    last_update = models.DateTimeField(auto_now_add=True, verbose_name='Dernier ajout')
    board = models.ForeignKey(Board, related_name='topics')
    starter = models.ForeignKey(User, related_name='topics')


class Post(models.Model):
    message = models.TextField(max_length=4000)
    topic = models.ForeignKey(Topic, related_name='posts')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='écrit le')
    updated_at = models.DateTimeField(null=True, verbose_name='édité le')
    created_by = models.ForeignKey(User, related_name='posts')
    updated_by = models.ForeignKey(User, null=True, related_name='+')




