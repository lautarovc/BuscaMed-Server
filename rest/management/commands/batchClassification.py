from django.core.management.base import BaseCommand, CommandError
from classifier import classifier
from datetime import datetime

class Command(BaseCommand):
	help = 'Loads tweets from all medicines'

	def handle(self, *args, **options):
		startTime = datetime.now()

		classifier.batchClassify()

		endTime = datetime.now() - startTime

		print(endTime)