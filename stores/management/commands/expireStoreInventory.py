from django.core.management.base import BaseCommand, CommandError
from stores.models import ProductosPorTienda
from datetime import datetime, timedelta, timezone
from django.conf import settings


class Command(BaseCommand):
	help = 'Erases expired inventory ('+str(settings.STORE_EXPIRATION)+' days old)'

	def handle(self, *args, **options):
		expiryDate = datetime.now(timezone.utc) - timedelta(days=settings.STORE_EXPIRATION)

		expiredInventory = ProductosPorTienda.objects.filter(fechaDeIngreso__lte=expiryDate)

		amount = len(expiredInventory)

		expiredInventory.delete()

		print(str(amount)+" deleted items. More than "+str(settings.STORE_EXPIRATION)+" days old.")