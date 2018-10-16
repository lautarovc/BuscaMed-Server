import pandas as pd
import re
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.externals import joblib
from sklearn.linear_model import LogisticRegression


def text_to_words(raw_text, medicines_regex, spanish_stops, stemmer):
    text = BeautifulSoup(raw_text, "html.parser").get_text()        #Removing HTML
    text = text.lower()                                             #Lower case everything
    letters_only = re.sub("[^a-záéíóúüñ]", " ", text)               #Removing punctuation
    medicines_found = re.findall(medicines_regex, letters_only)     #Finding all the medicines in the tweet
    letters_only = re.sub(medicines_regex, "meds", letters_only)    #Changing all specific medicine names to meds
    words = letters_only.split()                                    #Tokenizing
    meaningful_words = [w for w in words if not w in spanish_stops] #Removing stopwords
    meaningful_words = [stemmer.stem(w) for w in meaningful_words]  #Stemming the tweet
    return(" ".join(meaningful_words))                              #Returning it back as a string

medicines = pd.read_csv("../data/baseDatos-completa.csv", header=0, delimiter=",", engine = "python", encoding = "utf-8")  #Obtaining the medicines names from the file
medicines = list(set([w.lower() for w in medicines["nombre-marca"]])) #Putting them tidily into a list
medicines = re.compile(r"\b" + r"\b|\b".join(map(re.escape, medicines)) + r"\b") #Then making it into a regex

train = pd.read_csv("../data/tweetsClasificados-3000.csv", header=0, delimiter=";", engine = "python", encoding = "utf-8")  #Obtaining training data

num_tweets = train["text"].size #Getting the number of tweets
clean_train_tweets = [] #Initializing a list to clean them

stops = set(stopwords.words("spanish")) #Quicker to search in a set, so putting the stopwords in it

stemmer = SnowballStemmer("spanish")    #Initializing stemmer

for i in range(0, num_tweets):  #Cleaning all the training tweets
    clean_train_tweets.append(text_to_words(train["text"][i], medicines, stops, stemmer))

#Then we initialize the forest to train
vectorizer = CountVectorizer(strip_accents = "unicode", analyzer = "word", tokenizer = None, preprocessor = None, stop_words = None, max_features = 100)

train_text_features = vectorizer.fit_transform(clean_train_tweets)
train_text_features = train_text_features.toarray() #Arrays are easy to manipulate, plus we need this data structure

logistic_regression = LogisticRegression()
logistic_regression = logistic_regression.fit( train_text_features, train["cluster"] ) # Training logistic regression

joblib.dump(vectorizer, "vectorizer")
joblib.dump(logistic_regression, "logistic_regression")

#forest = RandomForestClassifier(n_estimators = 100) 
#forest = forest.fit(train_text_features, train["cluster"])  #Training the forest
#joblib.dump(vectorizer, "vectorizer")
#joblib.dump(forest, "forest")
