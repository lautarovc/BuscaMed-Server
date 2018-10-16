from django.core.management.base import BaseCommand, CommandError
from classifier import batchClassifier
from datetime import datetime

class Command(BaseCommand):
	help = 'Loads tweets from all medicines'

	def handle(self, *args, **options):
		startTime = datetime.now()

		batchClassifier.start_scrapping()

		endTime = datetime.now() - startTime

		print(endTime)