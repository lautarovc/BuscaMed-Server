from classifier.classifier import tweepy_auth

api = tweepy_auth()

dms = api.direct_messages()