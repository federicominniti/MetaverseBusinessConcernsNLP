import pickle

import numpy as np
import pandas as pd
import sklearn
import re

from sklearn.feature_extraction.text import TfidfVectorizer
features = pickle.load(open("./data/features.pkl", 'rb'))
loaded_model = pickle.load(open("./data/GaussianProcess.pkl", 'rb'))

print(features)
df = pd.DataFrame([])
df = pd.read_csv('cleaned_tweets.csv')

from sklearn.feature_extraction import text

punc = ['.', ',', '"', "'", '?', '!', ':', ';', '(', ')', '[', ']', '{', '}',"%"]
stop_words = text.ENGLISH_STOP_WORDS.union(punc)
desc = df.tokens_text.values
vectorizer = TfidfVectorizer(stop_words = stop_words)
X = vectorizer.fit_transform(desc)
words = vectorizer.get_feature_names()
df2 = pd.DataFrame(X.toarray(), columns=words)
df2 = df2[features]
print(df2)

df["GaussianProcess"] = loaded_model.predict(df2)

df.to_csv('./data/PostClassification.csv', sep=',', index=False)