import string

import snscrape.modules.twitter as sntwitter
import pandas as pd
import botometer
import sys

twitter_app_auth = {
                    'consumer_key': "C9gdI5bL2uOoQEIuV8Ff9WJvl",
                    'consumer_secret': "63qaemhFZTOZeUPNRLJN2vk3TYTYloTR7VHfs98jaZ8I71hJWf",
                    'access_token': "1430814108757209094-FubaZKRx1BSM39KlJSMdFMnntoEeiI",
                    'access_token_secret': "TiPBUwejHazVn5TpZb6ey1dsWgfg7XRcRty0Cj9CKkGdW"
                   }

botometer_api_url = "https://botometer-pro.p.rapidapi.com"

bom = botometer.Botometer(
                wait_on_ratelimit = True,
                botometer_api_url=botometer_api_url,
                rapidapi_key = "1c191fcea5msh1a9eabcbd080401p18a506jsn66fa9f188b6f",
                **twitter_app_auth)



def scrape_tweets(since, until, max, query):
    tweet_list = []
    query_string = query + " since:" + since + " until:" + until
    for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query_string).get_items()):
        if i > int(max):
            break
         
        if i % 1000 == 0:
          print("Scraped {} tweets".format(i))

        tweet_list.append([tweet.date, tweet.id, tweet.content, tweet.user.username])

    return tweet_list


def remove_bot_tweets(dataframe):
    BOT_THRESHOLD = 0.6
    bot_list = []
    usernames_to_test = dataframe["Username"].drop_duplicates().to_list()
    for screen_name, result in bom.check_accounts_in(usernames_to_test):
        bot_score = max(result['raw_scores']['english']['overall'], result['raw_scores']['universal']['overall'])
        if bot_score > BOT_THRESHOLD:
            bot_list.append(screen_name)
        print("@{0} = {1:.2f}".format(screen_name, bot_score))
    
    return dataframe[~dataframe['Username'].isin(bot_list)]


#STEP 1: SCRAPE TWEETS (OR RECOLLECT FROM CSV)
tweet_list = []
tweets_dataframe = pd.DataFrame([])
print(len(sys.argv))
if len(sys.argv) == 5:
    tweet_list = scrape_tweets(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    tweets_dataframe = pd.DataFrame(tweet_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
    tweets_dataframe.to_csv('text-query-tweets.csv', sep=',', index=False)
else:
    tweets_dataframe = pd.read_csv('tweets_final.csv')
    #Remove URL and NaN values
    tweets_dataframe = tweets_dataframe[~tweets_dataframe.Text.str.contains(r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)', na=False)]
    #tweets_dataframe = tweets_dataframe.sample(frac=0.1, replace=False, random_state=1)

print("done!")
# STEP 2: REMOVE TWEETS FROM BOTS
#tweets_dataframe = remove_bot_tweets(tweets_dataframe)

# STEP 3: NLP(TOKENIZATION, NORMALIZATION, FILTERING, STEMMING, DESTEMMING)
import re
from wordcloud import WordCloud
from unidecode import unidecode
from collections import Counter
from nltk.corpus import stopwords
from nltk.stem.porter import *

# create the wordcloud
def create_wordcloud(tweet_counter, filename):
    tweet_cloud = WordCloud(background_color = "white",
                        width = 1000,
                        height = 500,
                        relative_scaling = 0.5,
                        normalize_plurals = False).generate_from_frequencies(dict(tweet_counter.most_common(100)))
    tweet_cloud.to_file("./{}.png".format(filename))

def clean_text(text):
    # Remove twitter handlers
    text = re.sub('@[^\s]+', '', text)
    # remove hashtags
    text = re.sub(r'\B#\S+', '', text)
    # Remove all the special characters
    text = ' '.join(re.findall(r'\w+', text))
    # remove all single characters
    text = re.sub(r'\s+[a-zA-Z]\s+', '', text)
    # Substituting multiple spaces with single space
    text = re.sub(r'\s+', ' ', text, flags=re.I)

    #Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers.
    text = text.lower()
    text = re.sub('\[.*?\]', '', text)
    text = re.sub('[%s]' % re.escape(string.punctuation), '', text)
    text = re.sub('\w*\d\w*', '', text)

    #Get rid of some additional punctuation and non-sensical text that was missed the first time around.
    text = re.sub('[‘’“”…]', '', text)
    text = re.sub('\n', '', text)

    return text

def readlines():
    stopwords_file = open('stopwords.txt', 'r')
    lines = stopwords_file.readlines()
    # Strips the newline character
    stopwords = []
    for line in lines:
        stopwords.append(line.strip())
    return stopwords

STOPWORDS_EN = set(stopwords.words("english"))
file_stopwords = readlines()
STOPWORDS_EN = STOPWORDS_EN.union(set(file_stopwords))

STEMMER_EN = PorterStemmer()
#tweets_dataframe = tweets_dataframe[0:50000]

formatted_tweets = tweets_dataframe.to_dict('records')

merged_splitted = []
merged_normalized = []
merged_filtered = []
merged_stemmed = []
merged_destemmed = []
count = 0
for i in formatted_tweets:
    count = count + 1
    if count % 100 == 0:
        print(count)
    #if "http" not in i["Text"]:
    clean_text(i["Text"])
    tokens = re.split('\W+', i["Text"], flags=re.UNICODE)
    normalized = [unidecode(t.lower()) for t in tokens]
    filtered = [t for t in normalized if len(t) >= 3 and t not in STOPWORDS_EN]
    stemmed = [STEMMER_EN.stem(t) for t in filtered]

    stem_mapping = {}
    for f in filtered:
        stemmed_f = STEMMER_EN.stem(f)
        if stemmed_f not in stem_mapping:
            stem_mapping[stemmed_f] = Counter()
        stem_mapping[stemmed_f].update([f])

    i["tokens"] = [stem_mapping[t].most_common(1)[0][0] for t in stemmed]

    merged_splitted = merged_splitted + tokens
    merged_normalized = merged_normalized + normalized
    merged_filtered = merged_filtered + filtered
    merged_stemmed = merged_stemmed + stemmed
    merged_destemmed = merged_destemmed + i["tokens"]


create_wordcloud(Counter(merged_splitted), "wordcloud_1")
create_wordcloud(Counter(merged_normalized), "wordcloud_2")
create_wordcloud(Counter(merged_filtered), "wordcloud_3")
create_wordcloud(Counter(merged_stemmed), "wordcloud_4")
create_wordcloud(Counter(merged_destemmed), "wordcloud_5")

# 4
from transformers import pipeline
sentiment_analysis = pipeline("sentiment-analysis",model="siebert/sentiment-roberta-large-english")

# 0 -> positive
# 1 -> neutral
# 2 -> negative

tweets_dataframe["sentiment"] = 1
count = 0
def int_sentiment(row):
    global count
    count = count + 1
    if count % 10 == 0:
        print(count)
    res = sentiment_analysis(row["Text"])
    if res[0]["score"] > 0.6:
        if res[0]["label"] == 'POSITIVE':
            return 0
        else:
            return 2

tweets_dataframe["sentiment"] = tweets_dataframe.apply(lambda row : int_sentiment(row), axis= 1)

print(tweets_dataframe)

tweets_dataframe.to_csv('classified_tweets.csv', sep=',', index=False)