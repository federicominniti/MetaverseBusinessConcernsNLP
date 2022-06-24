import pickle

import numpy as np
import pandas as pd
import sklearn
import re

from sklearn.feature_extraction.text import TfidfVectorizer

loaded_model = pickle.load(open("gaussianProcess.pkl", 'rb'))

df = pd.DataFrame([])
df = pd.read_csv('cleaned_tweets.csv')

from sklearn.feature_extraction import text

punc = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}',"%"]
stop_words = text.ENGLISH_STOP_WORDS.union(punc)
desc = df.tokens_text.values
vectorizer = TfidfVectorizer(stop_words = stop_words,max_features = 56)
X = vectorizer.fit_transform(desc)
words = vectorizer.get_feature_names()
df2 = pd.DataFrame(X.toarray(), columns=words)

df["sentiment"] = loaded_model.predict(df2)

df.to_csv('classified_tweetsAAA.csv', sep=',', index=False)