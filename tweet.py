#pylint: disable=C0103, C0111, C0330, W0603
from __future__ import absolute_import, print_function #add this, must be here!
import asyncio
import logging
#import traceback
#import re
#from concurrent.futures import ProcessPoolExecutor
from datetime import datetime
import discord
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from tweepy.utils import import_simplejson
import config, util

#Authored by Renduras using discord.py and tweepy.py for the Slightly
#   Discordant group.
#Thanks to the admins: JD, Spirit, Saba, and Snaps;
#        and the mods: Shrekles and Foxx0rz;
# for maintaining a healthy and vibrant chat,
# and to SamIO for the Maibot base code.
#Also thanks to http://stackabuse.com/python-async-await-tutorial/

json = import_simplejson()

logging.basicConfig()
#logging.basicConfig(level=logging.DEBUG) #Uncomment for debugging

#KEYS
# Go to http://apps.twitter.com and create an app.
# The consumer key and secret will be generated for you after.
consumer_key = config.keys["twitter"]["consumer_key"]
consumer_secret = config.keys["twitter"]["consumer_secret"]

# After the step above, you will be redirected to your app's page.
# Create an access token under the the "Your access token" section.
access_token = config.keys["twitter"]["access_token"]
access_token_secret = config.keys["twitter"]["access_token_secret"]

#TWITTER HANDLES
#Admins, mods, and my twitter handles.
#twitter_feeds = ['Renduras', 'Princessnapped', 'Driftercolai',
#        'KingSabear', 'JDSalazar1230', 'shrekles420', 'teh_Foxx0rz']
#Test handles.
# twitter_users = ['Renduras']    #TESTING
# twitter_feeds = ['1352858526']  #TESTING
#Production handles.
# twitter_users = ['sdamned', 'KingSabear', 'Princessnapped', 'Renduras', 'teh_Foxx0rz', 'Wingu']
twitter_feeds = ['22467625', '2861293083', '2783451368', '1352858526', '3835979975', '1663215870']
twitter_users = config.tweet["twitter_feeds"]
# twitter_feeds = tweepy.api.lookup_users(screen_names=twitter_feeds) # further plans

#FILTER WORDS
#Tweets CONTAINING these words will be posted to Discord.
#Test filter.
# filter_words = ['test']
#Production filter.
filter_words = config.tweet["filter_words"]

#CHANNEL ID
#format = [[server1, channel1], [server2, channel2], etc.] #further plans
# channel_id = '316444984624676866' # test3255
# channel_id = '321570208651280396' # sdisco community-updates channel id
channel_id = config.main["alert_id"]

client = {}
async def init(client_bot):
    global client
    client = client_bot
    loop = client.loop
    asyncio.ensure_future(tweepy_login(), loop=loop)
    
# this should really go inside the discord listener class
async def tweepy_login():
    """Initial setup for twitter authentication and streaming.
    """
    discord_listener = DiscordListener()
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, discord_listener)

    #Positional arguments used because couldn't use async as a keyword
    # stream.filter(follow=twitter_feeds, track=filter_words, async=True)
    # filters tweets OR users, not AND
    # print("Starting Twitter data stream.")
    stream.filter(twitter_feeds, None, True, None, False, None, 'utf8', None)

class DiscordListener(StreamListener):
    """ A listener handles tweets that are received from the stream.
    This is a listener that forwards received tweets to discord.
    """

    # Checks that the data from the tweet is:
    #       - Not a retweet
    #       - Not a favorited tweet
    #       - Has a user that's in twitter_users
    #       - Has text
    #       - Has one of the filter words in that text.
    def tweet_filter(self, data):
        if 'retweeted' in data:
            if data['retweeted']:
                print("Retweeted in data.")
                return False

        if 'retweeted_status' in data:
            if data['retweeted_status']:
                print('Retweeted_status is not None.')
                return False

        if 'favorited' in data:
            if data['favorited']:
                print("Favorited in data.")
                return False

        if 'user' not in data:
            print("No user in data.")
            return False

        if 'screen_name' in data['user']:
            if data['user']['screen_name'] not in twitter_users:
                print("User is not in twitter_users.")
                return False

        if 'text' not in data:
            print("No text in data.")
            return False

        url_links = data
        if 'extended_tweet' in data:
            url_links = data['extended_tweet']

        if 'entities' in url_links:
            if 'urls' in url_links['entities']:
                for url in url_links['entities']['urls']: #how do you access a list again
                    if 'url' in url:
                        if 'https://t.co/AXtU4M0XWB' in url['url']: #picarto.tv for raizy
                            return True
                        if 'https://t.co/pfISgdBoUT' in url['url']: #picarto.tv for snaps
                            return True
                        if 'https://t.co/2UMYXiN4q9' in url['url']: #picarto.tv for saba
                            return True
                        if 'https://t.co/BXMAsZVIYi' in url['url']: #picarto.tv for fox
                            return True
                        if 'https://t.co/TEKYppvC8P' in url['url']: #picarto.tv for wingu
                            return True
                    if 'display_url' in url:
                        if 'picarto.tv' in url['display_url']:
                            return True
                    if 'expanded_url' in url:
                        if 'picarto.tv' in url['expanded_url']:
                            return True

        for i in filter_words:
            if i in data['text']:
                return True

        print("Probably not a stream tweet.")
        return False

    # Given formatted json data, returns the alert message.
    # Returns false if data not found.
    # IFTTT's formatting:
    #   @Renduras tweeted this at May 31, 2017 at 09:45 AM (PST):
    #   https://twitter.com/Renduras/status/871599288282783745
    def create_message(self, data):
        #https://stackoverflow.com/a/11717045
        username, screenname, date, id_str = (False,) * 4

        if 'name' in data['user']:
            username = data['user']['name']

        if 'screen_name' in data['user']:
            screenname = data['user']['screen_name']

        if 'timestamp_ms' in data:
            date = datetime.fromtimestamp(int(data['timestamp_ms']) // 1000
                    ).strftime('%b %d, %Y at %I:%M %p')

        if 'id_str' in data:
            id_str = data['id_str']

        if not username or not screenname or not date or not id_str:
            print("One or more of these not found in data: ")
            print("username: " + username)
            print("screenname: " + screenname)
            print("date: " + date)
            print("id_str: " + id_str)
            return False

        tweet = r'https://twitter.com/' + screenname + r'/status/' + id_str

        message = 'Meep meep!\n (' + username + ' tweeted this at ' + date \
                    + ' (PST):)\n' + tweet

        return message


    def on_data(self, raw_data):

        #Uncomment for testing - check if dl_output is empty
        #if dl_output == None:
        #    return False

        #Multiple output channels - needs more work
        #for i in dl_output:
        #    dl_server = util_get_server(i[0])
        #    dl_channel = util_get_channel(dl_server, i[1])

        # dl_server = util_get_server(dl_output[0])
        # dl_channel = util_get_channel(dl_server, dl_output[1])

        # alert_id is the id of the channel the bot will send its messages to.
        # dl_channel is the channel object.
        dl_channel = client.get_channel(channel_id)

        #uncomment for testing
        #print(raw_data)
        #print("---------------------------------------")

        print("---------------------------------------")
        print("Cleaning raw_data.")
        data = json.loads(raw_data)

        #uncomment for testing
        # if data:
            # print(data)
            # print("---------------------------------------")

        print("Filtering data.")
        if self.tweet_filter(data):
            print("Creating message.")
            message = self.create_message(data)
            try:
                print(data)
            except UnicodeDecodeError:
                print("Error while printing data: Unicode exception error.")

            if message:
                print("Sending message.\n")
                asyncio.ensure_future(client.send_message(dl_channel,
                    message), client.loop)
            print("\n")
        #uncomment for testing
        #else:
        #    print('no data found!')
        return True

    def on_error(self, status):
        print('-------------------------------------')
        print('\n')
        print('Twitter error:')
        print(status)
        print('\n')
        print('-------------------------------------')

        if status == 420:
            return False
