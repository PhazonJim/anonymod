import discord

#===Constants===#
CONFIG_FILE = os.path.join(os.path.dirname(__file__),"config.yaml")
CACHE_FILE =  os.path.join(os.path.dirname(__file__), "cache.json")

#===Globals===#
#Config file
config = None

client = discord.Client()
templates = {"1": "Test1", 
             "2": "Test2",
             "3": "Test3"}

def loadConfig():
    global config
    #Load configs
    try:
        config = yaml.load(open(CONFIG_FILE).read(), Loader=yaml.FullLoader)
    except:
        print("'config.yaml' could not be located. Please ensure 'config.example' has been renamed")
        exit()

@client.event
async def unpack_command(message):
    action, url, reply = message.content.split(' ')
    reply = templates[reply]

    response = ("If this was turned on, I would have:\n"
                "Used following action: {}\n"
                "On this comment: {}\n" 
                "With this message: {}\n").format(action, url, reply)
    print('hello')
    await message.channel.send(response)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    await client.process_commands(message)

@client.event
async def process_commands(message):
    if message.author == client.user:
        return

    if message.content.startswith('$'):
        await unpack_command(message)
    else:
        print(message.content)


loadConfig()

client.run(config['discord_key'])