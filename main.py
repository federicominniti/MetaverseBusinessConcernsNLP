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
        if i > max:
            break

        tweet_list.append(tweet.date, tweet.id, tweet.content, tweet.user.username)

    return tweet_list


def remove_bot_tweets(dataframe):
    BOT_THRESHOLD = 0.5
    bot_list = []
    scores_list = []
    usernames_to_test = dataframe["Username"].drop_duplicates().to_list()
    for screen_name, result in bom.check_accounts_in(usernames_to_test):
        bot_score = max(result['raw_scores']['english']['overall'], result['raw_scores']['universal']['overall'])
        scores_list.append(bot_score)
        if bot_score > BOT_THRESHOLD:
            bot_list.append(screen_name)
        print("@{0} = {1:.2f}".format(screen_name, bot_score))
    
    return dataframe[~dataframe['Username'].isin(bot_list)]



tweet_list = []
tweets_dataframe = pd.DataFrame([])
if len(sys.argv) == 5:
    tweet_list = scrape_tweets(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    tweets_dataframe = pd.DataFrame(tweet_list, columns=['Datetime', 'Tweet Id', 'Text', 'Username'])
    tweets_dataframe.to_csv('text-query-tweets.csv', sep=',', index=False)
else:
    tweets_dataframe = pd.read_csv('text-query-tweets.csv')


tweets_dataframe = remove_bot_tweets(tweets_dataframe)
