from django.core.management.base import BaseCommand, CommandError
from rest.models import Tweet
from datetime import datetime, timedelta, timezone
from django.conf import settings


class Command(BaseCommand):
	help = 'Erases expired tweets ('+str(settings.TWEET_EXPIRATION)+' days old)'

	def handle(self, *args, **options):
		expiryDate = datetime.now(timezone.utc) - timedelta(days=settings.TWEET_EXPIRATION)

		expiredTweets = Tweet.objects.filter(fecha__lte=expiryDate)

		amount = len(expiredTweets)

		expiredTweets.delete()

		print(str(amount)+" deleted tweets. More than "+str(settings.TWEET_EXPIRATION)+" days old.")

