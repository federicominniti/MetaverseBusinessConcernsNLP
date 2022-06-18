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
    tweet_cloud.to_file("./imgs/{}.png".format(filename))

STOPWORDS_EN = set(stopwords.words("english"))
STOPWORDS_EN.add('http')
STOPWORDS_EN.add('https')
STEMMER_EN = PorterStemmer()

formatted_tweets = tweets_dataframe.to_dict('records')

merged_splitted = []
merged_normalized = []
merged_filtered = []
merged_stemmed = []
merged_destemmed = []

for i in formatted_tweets:
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