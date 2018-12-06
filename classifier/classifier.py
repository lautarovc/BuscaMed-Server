import pandas as pd
import tweepy as tp
import sys, re, threading

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib

from rest import models
from django.conf import settings

######---------- VERSION 1.0 ----------######

medicines = pd.read_csv("data/baseDatos-completa.csv", header=0, delimiter=",", encoding = "utf-8")  #Obtaining the medicines names from the file
medicines_list = list(set([w.lower() for w in medicines["nombre-marca"]])) 						#Putting them tidily into a list
medicines = re.compile(r"\b" + r"\b|\b".join(map(re.escape, medicines_list)) + r"\b") 			#Then making it into a regex

stops = set(stopwords.words("spanish")) #Quicker to search in a set, so putting the stopwords in it

stemmer = SnowballStemmer("spanish")    #Initializing stemmer

forest = joblib.load('classifier/logistic_regression')	#Loading already trained logistic regression and initializing vectorizer
vectorizer = joblib.load('classifier/vectorizer')

#TOO MANY ISSUES WITH STREAMING, still here for archiving purposes
#class MyStreamListener(tp.StreamListener):	#Streamer for tweets
#	def on_status(self, status):	#What to do when it gets a tweet, we just classify it
#		classified = classify(status)
#
#	def on_error(self, status_code):	#In case of error, print code on screen
#		print(status_code)
#		return True

class Tweet:	#Tweet class for quicker and easier manipulation
	def __init__(self, url, text, medicines):	#Initially tweets only have their url, their cleaned text and the medicines found
		self.url = url
		self.text = text
		self.medicines = medicines

	def set_cluster(self, cluster):	#After classifying, they also have the cluster they belong to
		self.cluster = cluster

	def get_id(self):
		tweetId = self.url.split("/")[-1]
		return int(tweetId)

def tweepy_auth(keys):	#To initialize streaming api
	auth = tp.OAuthHandler(keys['consumer_key'], keys['consumer_secret'])
	auth.set_access_token(keys['access_token'], keys['access_secret'])
	api = tp.API(auth, wait_on_rate_limit = True, retry_count = 100, retry_delay = 10)
	return api

def clean(tweet):	#Takes a raw tweet directly from the streaming and cleans it for later use
	text = BeautifulSoup(tweet.text, "html.parser").get_text()	#First remove html tags
	text = text.lower()	#Then make everything lower case
	letters_only = re.sub("[^a-záéíóúüñ]", " ", text)	#Then eliminate all punctuation
	medicines_found = re.findall(medicines, letters_only)	#Then check which medicines are in it
	letters_only = re.sub(medicines, "meds", letters_only)	#Then replace all medicines with a generic word
	words = letters_only.split()	#Then split all the words to remove stops and stemming
	meaningful_words = [w for w in words if not w in stops]	#Removing stopwords
	meaningful_words = [stemmer.stem(w) for w in meaningful_words]	#Stemming
	return (Tweet("https://twitter.com/" + tweet.user.screen_name + "/status/" + str(tweet.id), " ".join(meaningful_words), medicines_found)) #Return a cleaned tweet

def classify(raw_tweet):	#Takes a raw tweet directly from streaming, cleans it and classifies it
	#print("Classifying tweet \"" + raw_tweet.text + "\"", end = " ")
	tweet = clean(raw_tweet)	#First clean the tweet
	features = vectorizer.transform([tweet.text])	#Extract its features
	features = features.toarray()	#Arrays are easier to manipulate
	result = forest.predict(features)	#Classify it, using the already loaded forest
	if not tweet.medicines:
		tweet.set_cluster(0)
	else:
		tweet.set_cluster(result[0])	#Set the result that was found
	#print("found in " + tweet.url + " with medicines " + str(tweet.medicines) + " as " + str(tweet.cluster))
	return tweet	#Finally return the classified tweet

#TOO MANY ISSUES, bandwidth, rate limits, query size limit, bandwidth concerns, still here for archiving purposes
#def start_streaming():	#Streaming tweets to constantly update the data base
#	api = tweepy_auth()	#Initialize the api
#	mSL = MyStreamListener()	#Initialize the streamer
#	mS = tp.Stream(auth = api.auth, listener = mSL)
#	mS.filter(track = medicines_list)	#Start the streaming filtering with medicines list

def batchClassify():	#Scrapping tweets, idea is do this about twice per day perhaps
	api = tweepy_auth(settings.TWITTER_AUTH[0])	#First initialize api
	medCount = 0
	for i in medicines_list:	#Then, do a query for each different medicine
		#print("Looking tweets with medicine " + i)	#This line for control purposes only
		medCount += 1
		print("\nMedicine "+str(medCount)+"/"+str(len(medicines_list)))
		found_tweets = api.search(q = i + "-filter:retweets", lang = "es")	#Get the list of tweets
		
		tweetCount = 0
		for j in found_tweets:	#Then classify all of the found tweets

			tweetCount += 1
			percent = (tweetCount * 100)/len(found_tweets)
			sys.stdout.flush()
			sys.stdout.write("\rProgress: "+str(percent)+"%")

			processed_tweet = (classify(j))
			if processed_tweet.cluster == 1:		#After they're classified, sort them out and throw them into the database
				found_medicine = models.Medicina.objects.filter(nombre = processed_tweet.medicines[0].upper())[0]
				new_tweet = models.Tweet(link = processed_tweet.url, clasificacion = "oferta", medicina = found_medicine)
				try:
					new_tweet.save()
				except:
					continue

			# Tweets asking for medicines not necessary
			# if processed_tweet.cluster == 2:
			# 	found_medicine = models.Medicina.objects.filter(nombre = processed_tweet.medicines[0].upper())[0]
			# 	new_tweet = models.Tweet(link = processed_tweet.url, clasificacion = "demanda", medicina = found_medicine)
			# 	try:
			# 		new_tweet.save()
			# 	except:
			# 		continue

######---------- FIN VERSION 1.0 ----------######

######---------- VERSION 2.0 ----------######

# Funcion que busca una lista de medicinas en Twitter
def listarTweets(medicine_list, from_id=None):
	api = tweepy_auth(settings.TWITTER_AUTH[0])
	medCount = 0 
	classified_tweets = []
	for i in medicine_list:	#Then, do a query for each different medicine
		
		medCount += 1
		print("\nMedicine "+str(medCount)+"/"+str(len(medicine_list)))
		if from_id:
			found_tweets = api.search(q = i.nombre + "-filter:retweets", lang = "es", since_id=from_id)	#Get the list of tweets
		else:
			found_tweets = api.search(q = i.nombre + "-filter:retweets", lang = "es")	#Get the list of tweets

		tweetCount = 0
		for j in found_tweets:	#Then classify all of the found tweets

			tweetCount += 1
			percent = (tweetCount * 100)/len(found_tweets)
			sys.stdout.flush()
			sys.stdout.write("\rProgress: "+str(percent)+"%")

			processed_tweet = (classify(j))
			if processed_tweet.cluster == 1:		#After they're classified, sort them out and throw them into the database
				found_medicine = models.Medicina.objects.filter(nombre = processed_tweet.medicines[0].upper())[0]
				new_tweet = models.Tweet(link = processed_tweet.url, clasificacion = "oferta", medicina = found_medicine)
				
				try:
					new_tweet.save()
					classified_tweets.append(new_tweet)
				except:
					continue

######---------- FIN VERSION 2.0 ----------######

######---------- VERSION 2.1 ----------######

# Hilo que busca una lista de medicinas en Twitter
class ListarThread(threading.Thread):
	def __init__(self, keys, medicine_list, from_id):
		threading.Thread.__init__(self)
		self.keys = keys
		self.medicine_list = medicine_list
		self.from_id = from_id

	def run(self):
		api = tweepy_auth(self.keys)
		medCount = 0 
		classified_tweets = []
		for i in self.medicine_list:	#Then, do a query for each different medicine
			
			medCount += 1
			print("\nMedicine "+str(medCount)+"/"+str(len(self.medicine_list)))
			if self.from_id:
				found_tweets = api.search(q = i.nombre + "-filter:retweets", lang = "es", since_id=self.from_id)	#Get the list of tweets
			else:
				found_tweets = api.search(q = i.nombre + "-filter:retweets", lang = "es")	#Get the list of tweets

			tweetCount = 0
			for j in found_tweets:	#Then classify all of the found tweets

				tweetCount += 1
				percent = (tweetCount * 100)/len(found_tweets)
				sys.stdout.flush()
				sys.stdout.write("\rProgress: "+str(percent)+"%")

				processed_tweet = (classify(j))
				if processed_tweet.cluster == 1:		#After they're classified, sort them out and throw them into the database
					found_medicine = models.Medicina.objects.filter(nombre = processed_tweet.medicines[0].upper())[0]
					new_tweet = models.Tweet(link = processed_tweet.url, clasificacion = "oferta", medicina = found_medicine)
					
					try:
						new_tweet.save()
						classified_tweets.append(new_tweet)
					except:
						continue

# Funcion que divide la lista de medicinas y busca en hilos de API keys distintos
def threadingTweets(keys, medicine_list, from_id=None):

	# Dividimos la lista en sublistas
	listSize = len(medicine_list)//len(keys)
	sizeMultiple = len(medicine_list)%len(keys) > 0

	if (listSize > 0):

		# Inicializamos fragmentos por cada API key
		fragments = [[] for i in range(len(keys))]
		i = 0

		# Agregamos medicina por fragmento
		for med in medicine_list:
			fragments[i].append(med)
			i += 1

			# Si ya hemos agregado a todos los fragmentos, reiniciamos contador
			if (i == len(keys)):
				i = 0

	else:
		fragments = [medicine_list[i] for i in range(len(medicine_list))]

	# Para cada fragmento y api key, creamos un hilo de busqueda de Twitter
	threads = []
	for i in range(len(fragments)):
		thread = ListarThread(keys[i], fragments[i], from_id)
		thread.start()
		print("Twitter thread #"+str(i))
		threads.append(thread)

	# Esperamos a que terminen los hilos
	for thread in threads:
		thread.join()

######---------- FIN VERSION 2.1 ----------######
