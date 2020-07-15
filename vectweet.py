#!/usr/bin/env python

import svgwrite
import textwrap
import argparse
import twitter
import json

# VecTweet by Robin Universe
# Licensed under BSD

try: # Try to load the config file
    with open('config.json') as config_file:
        config = json.load(config_file)
except:
    print("Failed to load config.json")
    exit()

parser = argparse.ArgumentParser() # set up arguments
parser.add_argument("--username",  "-u",  help="Specify a user to get the latest tweet of")
parser.add_argument("--tweet",     "-t",  help="Specify a tweet to convert")
parser.add_argument("--back",      "-b",  help="Show tweet before the latest tweet", type=int, default=1)
args = parser.parse_args()

user = config['account'] # if there is no user specified in the args, use the one saved in the config file
if args.username:
    user = args.username

def getTweet(username): # do twitter api stuff to get the latest tweet
    api = twitter.Api(consumer_key=config['ckey'],
                      consumer_secret=config['csecret'],
                      access_token_key=config['atoken'],
                      access_token_secret=config['asecret'])

    rawTweet = api.GetUserTimeline(screen_name=username, count=args.back)
    if args.tweet:
        id = args.tweet.rsplit('/', 1)[-1]
        rawTweet = api.GetStatus(id)
        return readTweet(rawTweet)
        
    return readTweet(rawTweet[args.back-1])

def readTweet(rawTweet): # Turn that into a smaller object for easier handling
    tweet = {}
    
    if rawTweet == "": # Checking to see if something borked
        print("No tweet data!")
        exit()

    if rawTweet.retweeted != "": # Keeps it from gobbling up RTs
        tweet = {
            'text' : rawTweet.text,
            'user' : "@" + rawTweet.user.screen_name,
            'handle' : rawTweet.user.name,
            'pfp' : rawTweet.user.profile_image_url
        }
        if rawTweet.media: # Adds the first media url if the post has it
            tweet.update( { 'media' : rawTweet.media[0].media_url } )

    print(tweet)
    return tweet

def createSVG(tweet):

    wrapper = textwrap.TextWrapper(width=35)       # Set up word wrapping on the tweet text
    string = wrapper.wrap(text=tweet['text'])

    # bits and bobs for controlling how everything is drawn
    offset       = 4.5                             # How far away the tweet text is from the Header stuff
    width        = len(string) * 30 + offset + 100 # Make the box longer depending on content
    height       = 500                             # yes these are flipped no I wont fix it
    borderRadius = 40                              # Make the box rounder?
    hoffset      = 25                              # Offsets from the top right corner for all content
    woffset      = 50
    bgcol        = 'black'                         # Background and mask color
    fgcol        = 'white'                         # Text color

    dwg = svgwrite.Drawing('tweet.svg', (height, width), profile='full')

    # All of this draws the bg. Couldnt figure out how to do rounded rectangles any other way 🥴
    dwg.add(dwg.circle(center=(borderRadius,        borderRadius),       r=borderRadius, fill=bgcol)) # Draw circles in each corner 
    dwg.add(dwg.circle(center=(borderRadius,        width-borderRadius), r=borderRadius, fill=bgcol))
    dwg.add(dwg.circle(center=(height-borderRadius, borderRadius),       r=borderRadius, fill=bgcol))
    dwg.add(dwg.circle(center=(height-borderRadius, width-borderRadius), r=borderRadius, fill=bgcol))

    dwg.add(dwg.rect((borderRadius, 0),            (height-(borderRadius*2), width),                  fill=bgcol)) # Fill up the rest of the space with rectangles
    dwg.add(dwg.rect((0,            borderRadius), (height,                  width-(borderRadius*2)), fill=bgcol))

    # Sets up the header
    dwg.add(dwg.image(tweet['pfp'], insert=(woffset+28, hoffset+5), size=(58,58)))                             # Link to profile picture
    dwg.add(dwg.circle(center=(woffset+57, hoffset+34), r=39, fill='none', stroke=bgcol, stroke_width=20))     # Circle mask over profile picture
    dwg.add(dwg.text(tweet['handle'], insert=(woffset+100, hoffset+33), fill=fgcol,  style='font-size:25px;')) # Handle
    dwg.add(dwg.text(tweet['user'],   insert=(woffset+100, hoffset+53), fill='grey', style='font-size:15px;')) # Username

    # Loops through the text wrapped version of the tweet text and makes new lines for each element
    for x in string: 
        dwg.add(dwg.text(x, insert=(woffset+30, 20 * offset + hoffset), fill=fgcol))
        offset = offset + 1
    dwg.save()

createSVG(getTweet(user))
exit()