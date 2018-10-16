from rest_framework import serializers
from .models import Tweet

class TweetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tweet
        fields = ('link', 'medicina')
        read_only_fields = ('link', 'medicina')