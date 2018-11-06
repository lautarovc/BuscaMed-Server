from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from django.contrib import messages
from django.shortcuts import redirect
from rest_framework import viewsets
from rest_framework.response import Response
from datetime import datetime, timezone

from .serializers import TweetSerializer, MedicinaSerializer, ActivoSerializer
from .models import *
from classifier import classifier
from webcrawler.webCrawlerFarmarket import webCrawler as webCrawlerFarmarket


from django.contrib.auth.models import User, Group


#----- HELPER FUNCTIONS -----#


# Usar esta lista para ignorar esas medicinas al buscar en el streaming (ayudan a reducir cantidad de tweets encontrados)

quitarComunes = ["CALCIO","ARANDA","OTAN","HIERRO","DUPLA","BICARBONATO","DIP",
					"FRICCION","CLORURO","REFRESH","EVRA","COST","FLUIR","MAILEN",
					"ADRENALINA","VICK","ALLER","VIAGRA","NOVA","VITAMINA C","ACTOS",
					"ZAP","NAS","KALI","CASTE","DOL","SAVER","SAGAL","RECITA","QUIN",
					"VENTUS", "TEMPRA", "SAX","VITAE","GABOX","ENAM","SELENE","SELES",
					"TARON", "CAMPAL","AZA","YAZ","KIR","CIFRAN","MIRENA","ENO","CLARIX",
					"PINAZO","ARNOL"]



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
				messages.add_message(medName, messages.ERROR, 'Disculpe, \'' + medName +'\' no es reconocido en nuestra base de datos.')
				template = loader.get_template('rest/index.html')				
				context = {'messages':messages}
				return (None,Medicina.objects.none(),True)

		return (activo,medicina,False)
	
	else:
		messages.add_message(medName, messages.ERROR, 'Disculpe, no puede dejar este campo vacío.')
		
		return (None,None,True)

# Aqui se hace lo de la busqueda de los tweets en la base de datos 
def retrieveTweets(listaMedicinas):
	listaTweets = Tweet.objects.none()
	for i in listaMedicinas:
		tweets = Tweet.objects.filter(medicina=i)
		listaTweets = listaTweets | tweets
	return listaTweets.order_by('-fecha')

# Funcion que se encarga de la busqueda de los tweets
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
		if ((edad.seconds/60) < 30):
			listaTweets = dbTweets

		# En caso contrario, se buscan nuevos tweets a partir del id del tweet mas reciente
		else:
			sinceId = dbTweets[0].getId()
			classifier.listarTweets(listaMedicinas, sinceId)

			listaTweets = retrieveTweets(listaMedicinas)

	# En caso contrario, se buscan tweets para cargar la base de datos
	else:
		classifier.listarTweets(listaMedicinas)
		listaTweets = retrieveTweets(listaMedicinas)

	medEncontrada = True
	return (listaTweets, medEncontrada)

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

class FarmarketWebViewSet(viewsets.ViewSet):

	def list(self, request):
		medicina = request.GET.get('med', None)

		if medicina:
			queryset = webCrawlerFarmarket('https://www.farmarket.com.ve/sitio/index.php/resultados-busqueda-productos/',medicina)

		else:
			queryset = []

		return Response(queryset)