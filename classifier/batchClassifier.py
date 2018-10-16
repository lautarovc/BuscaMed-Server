import pandas as pd
import tweepy as tp
import sys
import re

from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from rest import models
from classifier.twitterConfig import get_tokens


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

def tweepy_auth():	#To initialize streaming api
	consumer_keys, consumer_secret, access_token, access_secret = get_tokens()
	auth = tp.OAuthHandler(consumer_keys, consumer_secret)
	auth.set_access_token(access_token, access_secret)
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

def start_scrapping():	#Scrapping tweets, idea is do this about twice per day perhaps
	api = tweepy_auth()	#First initialize api
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
