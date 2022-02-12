import discord
import datetime
import threading
import os
import re
from io import StringIO
from contextlib import redirect_stdout
import requests  # For kanye quotes
from bs4 import BeautifulSoup


class Log:

  __slots__ = 'is_valid', 'content', 'author', 'attachments', 'embeds', 'created_at', 'deleted_at'

  # Initialize context structure
  def __init__(self, message):

    self.is_valid = message is not None

    if self.is_valid:

      # Save variables
      self.content = message.content
      self.author = message.author
      self.attachments = message.attachments
      self.embeds = message.embeds
      self.created_at = message.created_at

    self.deleted_at = datetime.datetime.now()


class Session:

  __slots__ = '_session'

  def __init__(self, session):
    self._session = session

  def get(self, session):
    r = self._session.get(session)
    if r.status_code == 429:
      return self.get(session)
    return r


class Student:
  __slots__ = 'name', 'image', 'school', 'url', 'id'
  def __init__(self, soup):
    self.name = soup.select_one('div.item-title > a').text
    self.image = soup.select_one('a > div > div > img')['src'].replace('imagecache/profile_sm', 'imagecache/profile_reg')
    self.school = soup.select_one('div.item-info > span.item-school').text
    self.url = 'https://mukilteo.schoology.com'+soup.select_one('div.item-title > a')['href']+'/info'
    self.id = None


class SchoologyView(discord.ui.View):

  def __init__(self, students, author):
    super().__init__()
    self.i = 0
    self.students = students
    self.author = author
    self.frst_button = discord.ui.Button(emoji='<:first:940169691425566741>')
    self.prev_button = discord.ui.Button(emoji='<:left:940157746723061810>')
    self.next_button = discord.ui.Button(emoji='<:right:940157728083570748>')
    self.last_button = discord.ui.Button(emoji='<:last:940169703177977866>')
    self.frst_button.callback = self.frst_callback
    self.prev_button.callback = self.prev_callback
    self.next_button.callback = self.next_callback
    self.last_button.callback = self.last_callback
    self.add_item(self.frst_button)
    self.add_item(self.prev_button)
    self.add_item(self.next_button)
    # self.add_item(self.last_button)
    self.disable_buttons()

  async def on_timeout(self):
    self.frst_button.disabled = \
    self.prev_button.disabled = \
    self.next_button.disabled = \
    self.last_button.disabled = True
    await self.message.edit(view=self)

  async def update(self, interaction):
    student = self.students[self.i]
    embed = interaction.message.embeds[0]
    embed.title = f'{student.name} ({self.i+1}/{len(self.students)})'
    embed.set_image(url=student.image)
    embed.set_footer(text=student.school)
    await interaction.message.edit(embed=embed, view=self)

  def disable_buttons(self):
    self.frst_button.disabled = \
    self.prev_button.disabled = \
    self.next_button.disabled = \
    self.last_button.disabled = False
    if self.i == 0:
      self.frst_button.disabled = \
      self.prev_button.disabled = True
    if self.i == len(self.students)-1:
      self.next_button.disabled = \
      self.last_button.disabled = True

  async def prev_callback(self, interaction):
    if interaction.user != self.author: return
    self.i -= 1
    self.disable_buttons()
    await self.update(interaction)

  async def next_callback(self, interaction):
    if interaction.user != self.author: return
    self.i += 1
    self.disable_buttons()
    await self.update(interaction)

  async def frst_callback(self, interaction):
    if interaction.user != self.author: return
    self.i = 0
    self.disable_buttons()
    await self.update(interaction)

  async def last_callback(self, interaction):
    if interaction.user != self.author: return
    self.i = len(self.students)-1
    self.disable_buttons()
    await self.update(interaction)



def get_session(username=os.environ['MSDUSERNAME'], password=os.environ['MSDPASSWORD']):

  try:
    # Login
    schoology_resp = requests.get('https://mukilteo.schoology.com')
    schoology_soup = BeautifulSoup(schoology_resp.content, features='lxml')
    login_resp = requests.post('https://sts.mukilteo.wednet.edu'+schoology_soup.find('form', {'id': 'loginForm'})['action'], {'UserName': username, 'Password': password})
    login_soup = BeautifulSoup(login_resp.content, features='lxml')
    login_soup_SAMLResponse = login_soup.find('form').find('input', {'name': 'SAMLResponse'})['value']

    s = requests.session()
    s.post('https://mukilteo.schoology.com/login/saml/receive', {'SAMLResponse': login_soup_SAMLResponse})

    return Session(s)

  except:
    return None



TOKEN = os.environ['TOKEN']
CLEAR_LIMIT = datetime.timedelta(minutes=30)
CLEAR_DELAY = datetime.timedelta(minutes=5)
SNIPE_DELAY = datetime.timedelta(seconds=60)
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif']

intents = discord.Intents.default()
intents.members = True
intents.messages = True
bot = discord.Client(intents=intents, status=discord.Status.dnd, activity=discord.Activity(name='"snipe"', type=2))
history = {}
admins = [557233155866886184]
s = get_session()
if not os.path.exists('tmp'): os.mkdir('tmp')


@bot.event
async def on_ready():

  # Bot is starting up
  print('[sniper] :: Logged in as', bot.user)

  # # Set bot status to 'Listening to "snipe"'
  # await bot.change_presence()

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
      async def __FUNCTION(message): print('__FUNCTION was not called')
      exec('async def __FUNCTION(message):\n  '+code.replace('\n', '\n  '), globals())
      with redirect_stdout(out): await __FUNCTION(message)
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

    # Message is available to snipe
    if message.channel.id in history:

      # Find deleted message
      ctx = history[message.channel.id].pop(0)

      # Clean channel history
      if len(history[message.channel.id]) == 0: del history[message.channel.id]

      # If message is invalid tell the user and terminate process
      if not ctx.is_valid:
        await message.channel.send('Message is unavailable (bot is being updated).')
        return


      # Resend exact message if message is embed sent by this bot (kinda useless ngl)
      if ctx.author == bot.user and len(ctx.embeds) != 0:
        embed = ctx.embeds[0]
        # Message has attachments
        if len(ctx.attachments) != 0:
          attachment = ctx.attachments[0]
          # Save attachment
          await attachment.save('tmp/'+attachment.filename)
          # Send embed with attachment
          await message.channel.send(embed=embed, file=discord.File('tmp/'+attachment.filename))
          # Remove temporary file
          os.remove('tmp/'+attachment.filename)
        # Message has no attachments
        else:
          # Resend this bot's embed
          await message.channel.send(embed=embed)
        return  # Message has just been sniped


      # Add data to embed
      embed = discord.Embed(description=ctx.content, color=0x202225) # 0xbb0a1e
      try: embed.set_author(name=ctx.author, icon_url=ctx.author.display_avatar.url)
      except: embed.set_author(name='Unknown User', icon_url=r'https://cdn.discordapp.com/embed/avatars/0.png')
      embed.timestamp = ctx.created_at

      # Message has attachments
      if len(ctx.attachments) != 0:

        attachment = ctx.attachments[0]

        # Save attachment
        await attachment.save('tmp/'+attachment.filename)

        # Put attachment inside of embed if it is image
        if any(attachment.filename.endswith(ext) for ext in IMAGE_EXTENSIONS):
          embed.set_image(url='attachment://'+attachment.filename)
          await message.channel.send(embed=embed, file=discord.File('tmp/'+attachment.filename))
          for embed in ctx.embeds: await message.channel.send(embed=embed)  # Deleted message's embeds

        # Send separately if attachment is not image
        else:
          await message.channel.send(embed=embed)
          for embed in ctx.embeds: await message.channel.send(embed=embed)  # Deleted message's embeds
          await message.channel.send(file=discord.File('tmp/'+attachment.filename))

        # Remove temporary file
        os.remove('tmp/'+attachment.filename)

      # Message has no attachments
      else:

        # Send this bot's embed
        await message.channel.send(embed=embed)

        # Send deleted message's embeds
        for embed in ctx.embeds: await message.channel.send(embed=embed)

    # No message to snipe
    else: await message.channel.send("There's nothing to snipe!")


  # User wants to doxx
  elif len(words) >= 3 and words[0] == 'pls' and (words[1] == 'dox' or words[1] == 'doxx'):

    if message.guild is not None and message.guild.id == 836698659071590452:
      await message.channel.send('Please use `/search <person>` instead next time, thanks!')
      if s is None: return

    if s is None:
      await message.channel.send('Sorry, this command is not working at the moment')
      return

    query = " ".join(words[2:])
    if len(query) < 3:
      await message.channel.send('Please use at least 3 letters')

    else:
      soup = BeautifulSoup(s.get(f'https://mukilteo.schoology.com/search/user?s={query}').content, features='lxml')
      if soup.select_one('#main-inner > div.item-list > ul > li.search-summary.first') is None:
        await message.channel.send("That person doesn't exist!")
      else:
        students = [
          Student(student)
          for student in soup.select('#main-inner > div.item-list > ul > li.search-summary > div')
        ]
        student = students[0]

        embed = discord.Embed(color=0x202225)
        embed.title = f'{student.name} (1/{len(students)})'
        embed.set_image(url=student.image)
        embed.set_footer(text=student.school)

        view = SchoologyView(students, message.author)
        view.message = await message.channel.send(embed=embed, view=view)


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

  # Message is in cache
  if payload.cached_message is not None:

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
  for filename in os.listdir('tmp'):
      os.remove('tmp/'+filename)

  # Create new session
  global s
  s = get_session()


# Start clearing memory (recursive thread)
mem_clear()

# Start bot on Discord
bot.run(TOKEN)
