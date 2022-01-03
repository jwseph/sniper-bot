import discord
import datetime
import threading
import os
import re
from io import StringIO
from contextlib import redirect_stdout
import requests  # For kanye quotes
import pickle as pkl


class Log:

    __slots__ = 'is_valid', 'presnipe_id', 'content', 'author', 'attachments', 'embeds', 'created_at', 'deleted_at'

    # Initialize context structure
    def __init__(self, message, presnipe_id = None):

        self.is_valid = message is not None

        if self.is_valid:

            # Save variables
            self.presnipe_id = presnipe_id
            self.content = message.content
            self.author = message.author
            self.attachments = message.attachments
            self.embeds = message.embeds
            self.created_at = message.created_at

        self.deleted_at = datetime.datetime.now()


async def snipe(ctx, channel):

    # Clean channel history
    if channel.id in history and len(history[channel.id]) == 0:
        del history[channel.id]

    # If message is invalid tell the user and terminate process
    if not ctx.is_valid:
        await channel.send('Message is unavailable (bot is being updated).')
        return


    # Resend exact message if message is embed sent by this bot (kinda useless ngl)
    if ctx.author == bot.user and len(ctx.embeds) != 0:
        embed = ctx.embeds[0]
        # Message has attachments
        if len(ctx.attachments) != 0:
            attachment = ctx.attachments[0]
            # Save attachment
            await attachment.save('temp/'+attachment.filename)
            # Send embed with attachment
            await channel.send(embed=embed, file=discord.File('temp/'+attachment.filename))
            # Remove temporary file
            os.remove('temp/'+attachment.filename)
        # Message has no attachments
        else:
            # Resend this bot's embed
            await channel.send(embed=embed)
        return  # Message has just been sniped


    # Add data to embed
    embed = discord.Embed(description=ctx.content, color=0x202225) # 0xbb0a1e
    try: embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url)
    except: embed.set_author(name='Unknown User', icon_url=r'https://cdn.discordapp.com/embed/avatars/0.png')
    # embed.set_footer(text=bot.user, icon_url=bot.user.avatar_url)
    embed.timestamp = ctx.created_at

    # Message has attachments
    if len(ctx.attachments) != 0:

        attachment = ctx.attachments[0]

        # Save attachment
        await attachment.save('temp/'+attachment.filename)

        # Put attachment inside of embed if it is image
        if any(attachment.filename.endswith(ext) for ext in IMAGE_EXTENSIONS):
            embed.set_image(url='attachment://'+attachment.filename)
            await channel.send(embed=embed, file=discord.File('temp/'+attachment.filename))
            for embed in ctx.embeds: await channel.send(embed=embed)  # Deleted message's embeds


        # Send separately if attachment is not image
        else:
            await channel.send(embed=embed)
            for embed in ctx.embeds: await channel.send(embed=embed)  # Deleted message's embeds
            await channel.send(file=discord.File('temp/'+attachment.filename))

        # Remove temporary file
        os.remove('temp/'+attachment.filename)

    # Message has no attachments
    else:

        # Send this bot's embed
        await channel.send(embed=embed)

        # Send deleted message's embeds
        for embed in ctx.embeds: await channel.send(embed=embed)

    # Increase snipe total
    global snipes
    snipes += 1
    open('count.txt', 'w').write(str(snipes))
    print(f'[sniper] :: Successful snipe! #{snipes}')


TOKEN = os.environ['TOKEN']
CLEAR_LIMIT = datetime.timedelta(minutes=30)
CLEAR_DELAY = datetime.timedelta(minutes=5)
SNIPE_DELAY = datetime.timedelta(seconds=60)
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif']

intents = discord.Intents.default()
intents.members = True
intents.messages = True
bot = discord.Client(intents=intents)
history = {}
admins = [557233155866886184]
with open('count.txt', 'r') as f: snipes = int(f.read())


@bot.event
async def on_ready():

    # Bot is starting up
    print('[sniper] :: Logged in as', bot.user)

    # Set bot status to 'Listening to "snipe"'
    await bot.change_presence(activity=discord.Activity(name='"snipe"', type=2))

    # # Cache old messages
    # for guild in bot.guilds:
    #     for channel in guild.text_channels:
    #         await channel.history().flatten()


@bot.event
async def on_message(message):

    # Stop execution if sender is this bot
    if message.author == bot.user: return

    # Execute message if it is send by admin and is enclosed with "```"s
    if message.author.id in admins and message.content.startswith('```') and message.content.endswith('```'):

        code = message.content[3:-3]

        try:

            # Execute whilst capturing stdout
            out = StringIO()
            with redirect_stdout(out): exec(code)
            str_out = out.getvalue()

            # Send stdout if there is anything to send
            if str_out != '' and not str_out.isspace():
                await message.channel.send(str_out)

        except Exception as e:

            # Send error message
            await message.channel.send(e)

        return

    # Find first word in string: re.sub(r"^\W+", "", mystring)
    # Find first 10 words in message
    words = [word.lower() for word in re.findall(r'\w+', message.content)][:10]


    # Disable and snipe are in words
    if 'disable' in words and 'snipe' in words or 'disablesnipe' in words:

        await message.channel.send("Please don't disable me! <:an:858788822427107348>")


    # "Snipe" is in the first 3 words
    elif 'snipe' in words[:3]:

        # Message was a reply (resend message)
        if message.reference is not None:
            print('sniping reply')

            await snipe(Log(message.reference.cached_message), message.reference.cached_message.channel)

        # Message is available to snipe
        elif message.channel.id in history:
            print('sniping normally')

            # Find deleted message
            ctx = history[message.channel.id].pop(0)

            # Snipe message
            await snipe(ctx, message.channel)

        # No message to snipe
        else: await message.channel.send("There's nothing to snipe!")


    elif 'presnipe' in words[:3]:
        print('presniping reply')

        # Message was a reply (save next message for autosniping)
        if message.reference is not None:

            # Log message that was replied to (must be in same channel btw)
            if message.channel.id in history:
                history[message.channel.id].append(Log(message.reference.cached_message, presnipe_id = message.reference.message_id))
            else:
                history[message.channel.id] = [Log(message.reference.cached_message, presnipe_id = message.reference.message_id)]


    # Kanye is in words
    elif 'kanye' in words or 'west' in words or ('wanye' in words and 'kest' in words):

        response = requests.get(r'https://api.kanye.rest/')
        while not response.ok: response = requests.get(r'https://api.kanye.rest/')

        quote = response.json()['quote']
        if quote[-1].isalpha(): quote += '.'

        embed = discord.Embed(description=quote, color=0x202225)
        embed.set_footer(text='- Kanye West')

        await message.channel.send(embed=embed)



async def on_raw_message_action(payload):

    # If message was presniped, autosnipe it
    if payload.channel_id in history:
        # Look through cached messages for channel
        channel = history[payload.channel_id]
        for i in range(len(channel)):

            # Presniped message was found in cache
            if channel[i] is not None and channel[i].presnipe_id == payload.message_id:
                print('sniping from deleted message')
                print(channel)
                # Store deleted presniped message
                ctx = channel.pop(i)

                # Send presniped message
                await snipe(ctx, bot.get_channel(payload.channel_id))

                # Stop searching
                break

    # Message is in cache
    elif payload.cached_message is not None:

        message = payload.cached_message

        # Bot can now snipe its own messages
        # # Stop execution if sender is this bot
        # if message.author == bot.user: return

        # Message has already been deleted recently (in channel)
        if message.channel.id in history and \
        history[message.channel.id][0].is_valid and \
        datetime.datetime.now()-history[message.channel.id][0].deleted_at < SNIPE_DELAY:

            # Put deleted message in queue
            history[message.channel.id].append(Log(message))

        # Sender has not deleted another message recently
        else:

            # Log message normally
            history[message.channel.id] = [Log(message)]

    # # Message is not in cache
    # else:

    #     # Log unless a valid deleted message is already saved
    #     if payload.channel_id not in history:

    #         # Log invalid message
    #         history[payload.channel_id] = [Log(None)]


@bot.event
async def on_raw_message_delete(payload): await on_raw_message_action(payload)


@bot.event
async def on_raw_message_edit(payload): await on_raw_message_action(payload)


def mem_clear():

    # Recurse
    thread = threading.Timer(CLEAR_DELAY.seconds, mem_clear)
    thread.daemon = True
    thread.start()

    # Get current time
    now = datetime.datetime.now()

    # Remove old logs from history
    for channel_id, log in history.copy().items():

        # Remove old logs until log is accepted  X--(history is sorted)--X
        if now-log[0].deleted_at > CLEAR_LIMIT:

            del history[channel_id]

        #if now-log[0].deleted_at < CLEAR_LIMIT: break
        #del history[channel_id]

    # Remove files from temp to free storage
    for filename in os.listdir('temp'):
        os.remove('temp/'+filename)


# Start clearing memory (recursive thread)
mem_clear()

# Start bot on Discord
bot.run(TOKEN)
