import discord
import yaml
import os
import praw

#===Constants===#
CONFIG_FILE = os.path.join(os.path.dirname(__file__),"config.yaml")
CACHE_FILE =  os.path.join(os.path.dirname(__file__), "cache.json")

#===Globals===#
#Config file
CONFIG = None
REDDIT = None
client = discord.Client()

def loadConfig():
    global CONFIG
    #Load configs
    try:
        CONFIG = yaml.load(open(CONFIG_FILE).read(), Loader=yaml.FullLoader)
    except:
        print("'config.yaml' could not be located. Please ensure 'config.example' has been renamed")
        exit()

def initReddit():
    client = CONFIG["client"]
    reddit = praw.Reddit(**client)
    return reddit

def check_for_duplicate_comments(commentObj):
    #Check top level comments in the submission object
    #commentObj.comments.replace_more(limit=0)
    for comment in commentObj.replies:
        if comment.distinguished:
            return True
    return False

def post_comment(permalink, reply_text):
    try:
        #get comment from URL
        target_comment = REDDIT.comment(url=permalink)
        target_comment.refresh()
        #check for duplicate comment
        if check_for_duplicate_comments(target_comment):
            return {"status": False, "err": "This comment already has a moderator reply under it.", "child_comment": None}
        #Leave a comment
        child_comment = target_comment.reply(reply_text)
        child_comment.mod.distinguish(how="yes",sticky=True)
        child_comment.mod.lock()
        return {"status": True, "child_comment": child_comment}
    except Exception as e:
        print (e)
        #If anything bad happens, return back false
        return {"status": False, "err": e, "child_comment": None}

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$'):
        await process_commands(message)

@client.event
async def process_commands(message):
    url = ''
    rule = ''
    templates = CONFIG["reply_template"]
    params = message.content.split(' ')
    if params[0][0] == '$':
        params[0] = params[0][1:]
    if len(params[0]) <= 3:
        rule, url = params
    else:
        url, rule = params
    reply = templates[rule]
    response = post_comment(url, reply)
    if response["status"]:
        mod_reply = response["child_comment"]
        discord_message = ( "Link to offending comment: {}\nLink to mod reply {}").format(url, mod_reply.permalink)
        await message.channel.send(discord_message)
    else:
        await message.channel.send(response["err"])

loadConfig()
REDDIT = initReddit()
moderator = REDDIT.subreddit(CONFIG["subreddit"]).mod
client.run(CONFIG['discord_key'])