from datetime import datetime, timezone, timedelta

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from rest_framework import viewsets
from rest_framework.response import Response
from django.contrib.auth.models import User, Group

from webcrawler.webCrawlerFarmarket import webCrawler as webCrawlerFarmarket
from webcrawler.webCrawlerFullFarmacia import webCrawler as webCrawlerFullFarmacia
from webcrawler.webCrawlerFundafarmacia import webCrawler as webCrawlerFundafarmacia
from classifier import classifier

import stores.models as store
import stores.serializers as storeSerializers
from .serializers import TweetSerializer, MedicinaSerializer, ActivoSerializer
from .models import *



#----- HELPER FUNCTIONS -----#


# Usar esta lista para ignorar esas medicinas al buscar en el streaming (ayudan a reducir cantidad de tweets encontrados)

quitarComunes = ["CALCIO","ARANDA","OTAN","HIERRO","DUPLA","BICARBONATO","DIP",
					"FRICCION","CLORURO","REFRESH","EVRA","COST","FLUIR","MAILEN",
					"ADRENALINA","VICK","ALLER","VIAGRA","NOVA","VITAMINA C","ACTOS",
					"ZAP","NAS","KALI","CASTE","DOL","SAVER","SAGAL","RECITA","QUIN",
					"VENTUS", "TEMPRA", "SAX","VITAE","GABOX","ENAM","SELENE","SELES",
					"TARON", "CAMPAL","AZA","YAZ","KIR","CIFRAN","MIRENA","ENO","CLARIX",
					"PINAZO","ARNOL"]

#----- TWITTER FUNCTIONS -----#

# Función que verifica que la medicina buscada por el usuario se encuentra en la base de datos, y devuelve equivalentes
def searchDataBase(medName):
	searchQuery = medName.upper()
	
	if searchQuery:
		# Se busca primero la medicina (es lo mas probable que se busque de primero)
		try:
			medicina = Medicina.objects.filter(nombre=searchQuery)
			if medicina:
				if type(medicina) is not Medicina:
					medicina = medicina[0]
			activo = Activo.objects.get(componente=medicina.activo)
			medicina = Medicina.objects.filter(activo=activo).order_by('nombre')
		except:
			try:
				activo = Activo.objects.get(componente=searchQuery)
				medicina = Medicina.objects.filter(activo=activo).order_by('nombre')
			except:
			
				return (None,Medicina.objects.none(),True)

		return (activo,medicina,False)
	
	else:
		
		return (None,None,True)

# Aqui se hace lo de la busqueda de los tweets en la base de datos 
def retrieveTweets(listaMedicinas):
	expiryDate = datetime.now(timezone.utc) - timedelta(days=3)

	listaTweets = Tweet.objects.none()
	for i in listaMedicinas:
		tweets = Tweet.objects.filter(medicina=i, fecha__gte=expiryDate)
		listaTweets = listaTweets | tweets
	return listaTweets.order_by('-fecha')

# Funcion que se encarga de la busqueda de los tweets en la BD
def buscaTweets(medName):

	# Se agregó lo de problema para casos en los que la persona escribia una medicina que no existia
	activo,listaMedicinas,problema = searchDataBase(medName)
	if problema:
		medEncontrada = False
		return (listaMedicinas, medEncontrada)

	# Se quitan aquellas medicinas con que son palabras comunes y que tienen otras medicinas "mas representativas"
	for i in quitarComunes:
		if i in listaMedicinas:
			listaMedicinas.remove(i)
			break
	listaTweets = retrieveTweets(listaMedicinas)

	medEncontrada = True
	return (listaTweets, medEncontrada)

# Funcion para buscar tweets directamente en Twitter
def buscaTwitter(medName):
	# Se agregó lo de problema para casos en los que la persona escribia una medicina que no existia
	activo,listaMedicinas,problema = searchDataBase(medName)
	if problema:
		medEncontrada = False
		return (listaMedicinas, medEncontrada)

	# Se quitan aquellas medicinas con que son palabras comunes y que tienen otras medicinas "mas representativas"
	for i in quitarComunes:
		if i in listaMedicinas:
			listaMedicinas.remove(i)
			break

	dbTweets = retrieveTweets(listaMedicinas)

	# Si hay tweets en la base de datos
	if dbTweets:
		edad = datetime.now(timezone.utc) - dbTweets[0].fecha

		# Si el tweet mas reciente fue hace menos de 30 minutos
		if ((edad.seconds/60) < settings.TWEET_UPDATE):
			listaTweets = dbTweets

		# En caso contrario, se buscan nuevos tweets a partir del id del tweet mas reciente
		else:
			sinceId = dbTweets[0].getId()
			#classifier.listarTweets(listaMedicinas, sinceId)
			classifier.threadingTweets(settings.TWITTER_AUTH, listaMedicinas, sinceId)

			listaTweets = retrieveTweets(listaMedicinas)

	# En caso contrario, se buscan tweets para cargar la base de datos
	else:
		#classifier.listarTweets(listaMedicinas)
		classifier.threadingTweets(settings.TWITTER_AUTH, listaMedicinas)

		listaTweets = retrieveTweets(listaMedicinas)

	medEncontrada = True
	return (listaTweets, medEncontrada)

#----- STORES FUNCTIONS -----#

def getComponent(medName):
	medName = medName.upper()
	
	if medName:
		# Revisamos si nos pidieron un componente activo
		activo = store.Activo.objects.filter(componente=medName)

		# Si no, revisamos si nos pidieron una medicina
		if len(activo) == 0:
			medicina = store.Medicina.objects.filter(nombre=medName)

			# Si no es ninguno, no es nada
			if len(medicina) == 0:
				return store.Activo.objects.none()

			# Obtenemos componente activo de la medicina
			activo = store.Activo.objects.filter(componente=medicina[0].activo.componente)

		return activo

	else:
		return store.Activo.objects.none()

def retrieveInventory(medName):

	if medName:
		activo = getComponent(medName)

		# Si no se consiguio el componente activo
		if len(activo) == 0:
			return store.ProductosPorTienda.objects.none()


		productos = store.ProductosPorTienda.objects.filter(producto__medicina__activo=activo[0])

	else:
		productos = store.ProductosPorTienda.objects.none()

	return productos

#----- VIEW CLASSES -----#
# Create your views here.

class TweetViewSet(viewsets.ReadOnlyModelViewSet):

	queryset = Tweet.objects.all()
	serializer_class = TweetSerializer

	#@action(detail=True)
	def list(self, request, pk=None):
		medicina = request.GET.get('med', None)

		if medicina:
			queryset, encontrada = buscaTwitter(medicina)

			if not encontrada:
				queryset = Tweet.objects.none()

		else:
			queryset = Tweet.objects.all()

		serializer = TweetSerializer(queryset, many=True)

		return Response(serializer.data)

class StoresViewSet(viewsets.ReadOnlyModelViewSet):

	queryset = store.ProductosPorTienda.objects.all()
	serializer_class = storeSerializers.InventorySerializer

	#@action(detail=True)
	def list(self, request, pk=None):
		medicina = request.GET.get('med', None)
		if medicina:
			queryset = retrieveInventory(medicina)

		else:
			queryset = store.ProductosPorTienda.objects.none()

		serializer = storeSerializers.InventorySerializer(queryset, many=True)

		return Response(serializer.data)

class WebViewSet(viewsets.ViewSet):

	def list(self, request):
		medicina = request.GET.get('med', None)

		if medicina:
			queryset = webCrawlerFarmarket('https://www.farmarket.com.ve/sitio/index.php/resultados-busqueda-productos/',medicina)
			queryset2 = webCrawlerFullFarmacia(medicina)
			queryset3 = webCrawlerFundafarmacia('http://www.fundafarmacia.com/consulta/busqueda.php', medicina)
			queryset += queryset2 + queryset3
		else:
			queryset = []

		return Response(queryset)