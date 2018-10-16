from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from .models import Activo, Medicina, Presentacion, Tweet
import urllib.request, json
from django.contrib import messages
from django.shortcuts import redirect

# Create your views here.

# Usar esta lista para ignorar esas medicinas al buscar en el streamming (ayudan a reducir cantidad de tweets encontrados)

quitarComunes = ["CALCIO","ARANDA","OTAN","HIERRO","DUPLA","BICARBONATO","DIP",
					"FRICCION","CLORURO","REFRESH","EVRA","COST","FLUIR","MAILEN",
					"ADRENALINA","VICK","ALLER","VIAGRA","NOVA","VITAMINA C","ACTOS",
					"ZAP","NAS","KALI","CASTE","DOL","SAVER","SAGAL","RECITA","QUIN",
					"VENTUS", "TEMPRA", "SAX","VITAE","GABOX","ENAM","SELENE","SELES",
					"TARON", "CAMPAL","AZA","YAZ","KIR","CIFRAN","MIRENA","ENO","CLARIX",
					"PINAZO","ARNOL"]


# Función que verifica que la medicina buscada por el usuario se encuentra en la base de datos
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
				messages.add_message(request, messages.ERROR, 'Disculpe, \'' + medName +'\' no es reconocido en nuestra base de datos.')
				template = loader.get_template('app/index.html')				
				context = {'messages':messages}
				return (None,redirect('/app',context),True)
		return (activo,medicina,False)
	
	else:
		messages.add_message(request, messages.ERROR, 'Disculpe, no puede dejar este campo vacío.')
		template = loader.get_template('app/index.html')				
		context = {'messages':messages}
		return (None,redirect('/app',context),True)

# Aqui se hace lo de la busqueda de los tweets en la base de datos 
def retrieveTweets(listaMedicinas):
	listaTweets = []	
	for i in listaMedicinas:
		tweets = Tweet.objects.filter(medicina=i)
		for j in tweets:
			listaTweets.append(j.link)
	return listaTweets

# Funcion que se encarga de la busqueda de los tweets
def buscaTweets(medName):
	# Se agregó lo de problema para casos en los que la persona escribia una medicina que no existia
	activo,listaMedicinas,problema = searchDataBase(medName)
	if problema:
		return listaMedicinas
	# Se quitan aquellas medicinas con que son palabras comunes y que tienen otras medicinas "mas representativas"
	for i in quitarComunes:
		if i in listaMedicinas:
			listaMedicinas.remove(i)
			break
	listaTweets = retrieveTweets(listaMedicinas)
