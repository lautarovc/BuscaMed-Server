from django.core.management.base import BaseCommand, CommandError
from rest.models import Tweet
from datetime import datetime, timedelta, timezone

class Command(BaseCommand):
	help = 'Erases expired tweets (3 days old)'

	def handle(self, *args, **options):
		expiryDate = datetime.now(timezone.utc) - timedelta(days=3)

		expiredTweets = Tweet.objects.filter(fecha__lte=expiryDate)

		amount = len(expiredTweets)

		expiredTweets.delete()

		print(str(amount)+" deleted tweets.")

