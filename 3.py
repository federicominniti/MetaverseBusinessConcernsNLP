from transformers import pipeline
sentiment_analysis = pipeline("sentiment-analysis",model="siebert/sentiment-roberta-large-english")

# 0 -> positive
# 1 -> neutral
# 2 -> negative

tweets_dataframe["sentiment"] = 1

def int_sentiment(row):
    res = sentiment_analysis(row["Text"])
    if res[0]["score"] > 0.6:
        if res[0]["label"] == 'POSITIVE':
            return 0
        else:
            return 2

tweets_dataframe["sentiment"] = tweets_dataframe.apply(lambda row : int_sentiment(row), axis= 1)

tweets_dataframe.to_csv('classified_tweets.csv', sep=',', index=False)
