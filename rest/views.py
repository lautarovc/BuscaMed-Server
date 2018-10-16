from django.shortcuts import render
from rest_framework import viewsets
from .serializers import TweetSerializer
from django.contrib.auth.models import User, Group
from .models import *

# Create your views here.
class TweetViewSet(viewsets.ReadOnlyModelViewSet):

    queryset = Tweet.objects.all()
    serializer_class = TweetSerializer