#!/usr/bin/python
# DochBot
# Version: 1.1

import praw
import argparse

# Take arguments
# Note - Reddit secret has leading '-' which screws with argument parsing. Must remain as last argument.

parser = argparse.ArgumentParser(description='Searches for strings and posts to reddit')
parser.add_argument('Username', type=str, help='Reddit Username')
parser.add_argument('Password', type=str, help='Reddit Password')
parser.add_argument('UserAgent', type=str, help='Reddit application name')
parser.add_argument('cID', type=str, help='Reddit application ID')
parser.add_argument('cSC', type=str, nargs=argparse.REMAINDER, help='Reddit application Secret')

args = parser.parse_args()

# Pulls cSC value from list and converts it to str - any additional arguments will be lost

args.cSC = str(args.cSC[0])

# Create reddit object utilising arguments

reddit = praw.Reddit(user_agent=args.UserAgent, client_id=args.cID, client_secret=args.cSC, username=args.Username,
                     password=args.Password)

# Set some global variables

subreddits = {"testingground4bots"}  # makes a set of subreddits you want to monitor

keywords = {"test"}  # makes a set of keywords to find in subreddits

bot_phrase = "I'm a bot and I'm searching for the word 'test'"  # phrase that the bot replies with

numFound = 0


# have some fun-ctions

def replace_more_comments(target):
    try:
        submission.comments.replace_more()
    except:
        print(" - Replace_more didn't work")

def print_positive_match(word, title, selftext, body):
    # Print details of positive match to terminal
    print()
    print(" - Here are the details of the match of phrase:", word,)
    print()
    print("Title:", title)
    print("Selftext:", selftext)
    print("Body:", body)
    print()
    print(" - I'm going to say:", bot_phrase)


def reply_to(target):
    # Replies to target
    #target.reply(bot_phrase)
    print(" - I replied")
    print()
    print("-------------------------------")


def check_duplicates(target):
    # Checks immediate child item for duplicate posts
    print()
    print(" - Match found, checking for replies containing bot phrase")
    print(" - First I'll make sure I'm not replying to myself")
    try:
        if bot_phrase in target.body:
            print(" - Myself or someone else has already said this, stopping now")
            print()
            print("-------------------------------")
            return True
    except:
        print(" - This is a post, and I don't make posts")

    print(" - Now I'll check comments")
    try:
        for i in target.comments:
            n_body = i.body.lower()
            #print("Checking comment '",n_body,"' for string", bot_phrase)
            if bot_phrase in n_body:
                print(" - Duplicate found in comment, stopping search")
                print()
                print("-------------------------------")
                return True
    except:
        print(" - There are no comments, now I'll check replies")
        for i in target.replies:
            n_body = i.body.lower()
            #print("Checking reply '", n_body, "' for string", bot_phrase)
            if bot_phrase in n_body:
                print(" - Duplicate found in reply, stopping search")
                print()
                print("-------------------------------")
                return True
    print(" - I didn't find any duplicates")
    return False


def recursive_search_replies(target):
    # cycle through child objects and match keywords exhaustively
    # First tries to match keywords
    if match_keywords_in_target(target) is True:
        return True

    # Then search all child items exhaustively (replies to replies etc.)
    for reply in target.replies:
        replace_more_comments(reply)
        if recursive_search_replies(reply) is True:
            return True


# TODO
def match_keywords_in_target(target):
    # match title, body, selftext or link in target (post, comment or reply)

    # Convert to lower and add exceptions for non-existent fields
    try:
        n_title = target.title.lower()
    except:
        n_title = ""

    try:
        n_selftext = target.selftext.lower()
    except:
        n_selftext = ""

    try:
        n_body = target.body.lower()
    except:
        n_body = ""
    #TODO - Add link search

    # Iterates through keywords to check for matches in target
    for word in keywords:
        if ((word in n_title) or (word in n_selftext) or (word in n_body)) and (check_duplicates(target) is False):
            print_positive_match(word, n_title, n_selftext, n_body)
            #reply_to(target)
            return True

# Main script
# Cycle through subreddits from list

print()
print("-------------------------------")
print()
print("Beep Boop I'm a bot doing bot things")
print()
print("-------------------------------")
print()

for subreddit in subreddits:
    target_subreddit = reddit.subreddit(subreddit)
    for submission in target_subreddit.new(limit=50):
        replace_more_comments(submission)
        if match_keywords_in_target(submission) is True:
            numFound = numFound + 1
        for comment in submission.comments:
            replace_more_comments(comment)
            if match_keywords_in_target(comment) is True:
                numFound = numFound + 1
            for reply in comment.replies:
                replace_more_comments(reply)
                if recursive_search_replies(reply) is True:
                    numFound = numFound + 1

# Notify if any matches were found
if numFound == 0:
    print()
    print("**** I finished without posting anything, bye ****")
    print()
    print("-------------------------------")
else:
    print()
    print("**** I replied to", numFound, "items. Bye ****")
    print()
    print("-------------------------------")
