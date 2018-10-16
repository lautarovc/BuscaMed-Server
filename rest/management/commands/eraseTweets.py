from django.core.management.base import BaseCommand, CommandError
from rest.models import Tweet
from datetime import datetime

class Command(BaseCommand):
	help = 'Erases all tweets from database'

	def handle(self, *args, **options):
		startTime = datetime.now()

		Tweet.objects.all().delete()

		endTime = datetime.now() - startTime

		print(endTime)