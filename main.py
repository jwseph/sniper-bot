import discord
import datetime
import threading
import os
import re
from io import StringIO
from contextlib import redirect_stdout
import requests  # For kanye quotes
from bs4 import BeautifulSoup
import json
import asyncio
import random

from uwuify import uwuify
from rtdb import ref, increment


class Log:

  __slots__ = 'is_valid', 'content', 'author', 'attachments', 'embeds', 'color', 'created_at', 'deleted_at'

  # Initialize context structure
  def __init__(self, message, color=0x202225):

    self.is_valid = message is not None

    if self.is_valid:

      # Save variables
      self.content = message.content
      self.author = message.author
      self.attachments = message.attachments
      self.embeds = message.embeds
      self.color = color
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
  def __init__(self, obj=None, **kwargs):
    if 'soup' in kwargs:
      soup = kwargs['soup']
      self.name = soup.select_one('div.item-title > a').text
      self.image = [soup.select_one('a > div > div > img')['src'].replace('imagecache/profile_sm', 'imagecache/profile_reg')]
      self.school = [soup.select_one('div.item-info > span.item-school').text]
      self.url = 'https://mukilteo.schoology.com'+soup.select_one('div.item-title > a')['href']+'/info'
      self.id = None
    elif obj is not None:
      self.name = obj['name']
      self.image = obj['image']
      self.school = obj['school']
      self.url = obj['url']
      self.id = obj['id']
    else:
      raise ValueError('Neither soup or obj was passed in Student constructor.')
  def to_dict(self):
    return {
      'name': self.name,
      'image': self.image,
      'school': self.school,
      'url': self.url,
      'id': self.id
    }
def to_dict(student: Student):
  return student.to_dict()


class SchoologyView(discord.ui.View):

  SCHOOL_URLS = {
    'Mukilteo School District': 'https://www.mukilteoschools.org/',
    'ACES': 'https://www.mukilteoschools.org/ac',
    'Challenger': 'https://www.mukilteoschools.org/ch',
    'Columbia': 'https://www.mukilteoschools.org/co',
    'CBTC': 'https://www.mukilteoschools.org/Page/336',
    'Discovery': 'https://www.mukilteoschools.org/di',
    'ECEAP': 'https://www.mukilteoschools.org/page/12058',
    'Endeavour': 'https://www.mukilteoschools.org/en',
    'Explorer': 'https://www.mukilteoschools.org/ex',
    'Fairmount': 'https://www.mukilteoschools.org/fa',
    'Harbour Pointe': 'https://www.mukilteoschools.org/hp',
    'Horizon': 'https://www.mukilteoschools.org/hz',
    'Kamiak': 'https://www.mukilteoschools.org/ka',
    'Lake Stickney': 'https://www.mukilteoschools.org/ls',
    'Mariner': 'https://www.mukilteoschools.org/ma',
    'Mukilteo Elementary': 'https://www.mukilteoschools.org/me',
    'Special Education': 'https://www.mukilteoschools.org/page/1194',
    'Virtual Academy': 'https://www.mukilteoschools.org/mva',
    'Odyssey': 'https://www.mukilteoschools.org/oe',
    'Olivia Park': 'https://www.mukilteoschools.org/op',
    'Olympic View': 'https://www.mukilteoschools.org/ov',
    'Pathfinder': 'https://www.mukilteoschools.org/pkc',
    'Picnic Point': 'https://www.mukilteoschools.org/pi',
    'Serene Lake': 'https://www.mukilteoschools.org/sl',
    'Sno-Isle Skills Center': 'https://snoisletech.com/',
    'Summer School - Elementary': 'https://www.mukilteoschools.org/Page/12059',
    'Summer School - Middle/High': 'https://www.mukilteoschools.org/Page/12059',
    'Summer School - Skills Center': 'https://www.mukilteoschools.org/Page/12059',
    'Voyager': 'https://www.mukilteoschools.org/vo',
  }

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
    self.embed = discord.Embed(color=0x202225)
    self.update_embed()

  async def on_timeout(self):
    self.frst_button.disabled = \
    self.prev_button.disabled = \
    self.next_button.disabled = \
    self.last_button.disabled = True
    try: await self.message.edit(view=self)
    except discord.errors.NotFound: print("SchoologyView message was already deleted")

  def update_embed(self):
    student = self.students[self.i]
    self.embed.title = f'{student.name}'
    self.embed.description = \
      (f'{"Student" if student.id.isdigit() else "Teacher"} ID: [{student.id}](https://mailto.kamiak.org/{student.id})' if student.id is not None else '')+'\n'\
      f'School: [{student.school[-1]}]({SchoologyView.SCHOOL_URLS.get(student.school[-1], "https://www.mukilteoschools.org/")})'
    self.embed.set_image(url=student.image[-1])
    self.embed.set_footer(text=f'{self.i+1} / {len(self.students)}')

  async def update(self, interaction):
    self.update_embed()
    await interaction.response.edit_message(embed=self.embed, view=self)

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
    # if interaction.user != self.author: return
    self.i -= 1
    self.disable_buttons()
    await self.update(interaction)

  async def next_callback(self, interaction):
    # if interaction.user != self.author: return
    self.i += 1
    self.disable_buttons()
    await self.update(interaction)

  async def frst_callback(self, interaction):
    # if interaction.user != self.author: return
    self.i = 0
    self.disable_buttons()
    await self.update(interaction)

  async def last_callback(self, interaction):
    # if interaction.user != self.author: return
    self.i = len(self.students)-1
    self.disable_buttons()
    await self.update(interaction)


class MudaeView(discord.ui.View):

  def __init__(self, student:Student):
    super().__init__()
    self.student = student
    self.button = discord.ui.Button(emoji='<:heart1:1024122660726259743>')
    self.button.callback = self.on_claim
    self.add_item(self.button)
    # Create embed
    self.embed = discord.Embed(color=0xff9c2c)
    self.embed.title = f'{student.name}'
    self.embed.description = \
      (f'{"Student" if student.id.isdigit() else "Teacher"} ID: [{student.id}](https://mailto.kamiak.org/{student.id})' if student.id is not None else '')+'\n'\
      f'School: [{student.school[-1]}]({SchoologyView.SCHOOL_URLS.get(student.school[-1], "https://www.mukilteoschools.org/")})'+'\n'\
      f'Click the button to claim!'
    self.embed.set_image(url=student.image[-1])

  async def on_timeout(self):
    self.button.disabled = True
    try: await self.message.edit(view=self)
    except discord.errors.NotFound: print("MudaeView message was already deleted")

  async def on_claim(self, interaction:discord.Interaction):
    self.button.disabled = True
    self.embed.color = 0x670d08
    self.embed.description = self.embed.description.replace('\nClick the button to claim!', '')
    self.embed.set_footer(text=f'Belongs to {interaction.user.display_name}', icon_url=interaction.user.display_avatar.url)
    await interaction.response.edit_message(embed=self.embed, view=self)



TOKEN = os.environ['TOKEN']
CLEAR_LIMIT = datetime.timedelta(minutes=30)
CLEAR_DELAY = datetime.timedelta(minutes=5)
SNIPE_DELAY = datetime.timedelta(seconds=60)
IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif']

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True
bot = discord.Client(intents=intents, status=discord.Status.do_not_disturb, activity=discord.Activity(name='"snipe"', type=2))
history = {}
admins = [557233155866886184]
data = [Student(student) for student in json.load(open('data.json', 'r')).values()] # Schoology data
data_school = {}  # Students per school
for student in data:
  if student.school[-1] not in data_school: data_school[student.school[-1]] = []
  data_school[student.school[-1]].append(student)
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
  # if message.author == bot.user: return

  # Execute message if it is send by admin and is enclosed with "```"s
  if message.author.id in admins and message.content.startswith('```') and message.content.endswith('```'):

    code = message.content[3:-3]

    try:

      # Execute whilst capturing stdout
      out = StringIO()
      exec('async def __FUNCTION(message):\n  '+code.replace('\n', '\n  '), globals())
      with redirect_stdout(out): await __FUNCTION(message)  # type: ignore
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

    # if message.author == bot.user: await message.delete()

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

      try:

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
        embed = discord.Embed(description=ctx.content, color=ctx.color) # 0xbb0a1e
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

      except discord.errors.Forbidden as e:

        # Put message back in cache if it was sniped while bot was muted or something
        if message.channel.id in history:

          # Insert at position 0 if array exists
          history[message.channel.id].insert(0, ctx)

        # Channel does not have a queue in history yet
        else:

          # Create a new array for channel with message
          history[message.channel.id] = [ctx]



    # No message to snipe
    else: await message.channel.send("There's nothing to snipe!")


  # User wants to doxx
  elif len(words) >= 3 and words[0] == 'pls' and (words[1] == 'dox' or words[1] == 'doxx'):

    # if message.guild is not None and message.guild.id == 836698659071590452:
    #   await message.channel.send('Please use `/search <person>` instead next time, thanks!')

    query = message.content.lower().split(' ')[2:]
    students = [
      student
      for student, matches in sorted(
        [
          (student, matches)
          for student in data
          for matches in [sum(
            sum(
              (10000 if len(param) == len(name) else 1)*(5*(len(query)-param_i))
              for name in student.name.lower().split(' ')
              if param in name
            )
            for param_i, param in enumerate(query)
          )]
          if matches > 0
        ],
        key=(lambda x: x[1]),
        reverse=True
      )
    ]
    if len(students) == 0:
      await message.channel.send("That person doesn't exist!")
    else:
      view = SchoologyView(students, message.author)
      view.message = await message.channel.send(embed=view.embed, view=view)
      ref.child(f'waifus/{students[0].url[::-1].split("/", 2)[1][::-1]}/doxxes').transaction(increment)
  
  
  # User wants to roll
  elif len(words) >= 2 and words[0] == 'pls' and words[1] in ['roll', 'r', 'kamiak', 'k', 'mariner', 'm']:

    # Return if user is using command in dms
    if isinstance(message.channel, discord.DMChannel):
      await message.channel.send('This command can only be used from a server!')
      return
    
    # Roll student
    if len(words) == 2:
      if words[1] in ['roll', 'r']: student = random.choice(data)
      elif words[1] in ['kamiak', 'k']: student = random.choice(data_school['Kamiak'])
      elif words[1] in ['mariner', 'm']: student = random.choice(data_school['Mariner'])
    else:
      s = ' '.join(words[2:])
      school = data_school.get(s.title(), data_school.get(s.upper(), None))
      if school == None:
        await message.channel.send('School couldn\'t be found. The full command is `pls roll <school>` without the High/Middle School at the end.')
        return
      student = random.choice(data_school[school])
    
    # Send embed
    view = MudaeView(student)
    view.message = await message.channel.send(embed=view.embed, view=view)

    
  # User wants to uwu text
  elif message.content.startswith('pls uwu '):
    await message.channel.send(uwuify(message.content[8:]))

  # User wants to uwuify text
  elif message.content.startswith('pls uwuify '):
    await message.channel.send(uwuify(message.content[11:]))


  # User wants to be reminded
  elif message.content.startswith('pls remind '):
    try:
      time, text = message.content[11:].split(' ', 1)
      number = float(time[:-1])
      seconds = number*{'s': 1, 'm': 60, 'h': 3600, 'd': 86400, 'w': 604800, 'y': 31557600}[time[-1].lower()]
    except:
      await message.channel.send("Sorry, I couldn't understand")
      return
    await message.channel.send(f"Reminding in {seconds} seconds...")
    await asyncio.sleep(seconds)
    await message.channel.send(f'<@{message.author.id}> {text}')


  # Kanye is in words
  elif 'kanye' in words or 'west' in words or ('wanye' in words and 'kest' in words):

    response = requests.get(r'https://api.kanye.rest/')
    while not response.ok: response = requests.get(r'https://api.kanye.rest/')

    quote = response.json()['quote']
    if quote[-1].isalpha(): quote += '.'

    embed = discord.Embed(description=quote, color=0x202225)
    embed.set_footer(text='- Kanye West')

    await message.channel.send(embed=embed)

  
  # 'pls waifu' command
  elif words[:2] == ['pls', 'waifu'] or words[:2] == ['pls', 'w']:
   
    response = requests.get(r'https://api.waifu.im/random?selected_tags=waifu')
    while not response.ok: response = requests.get(r'https://api.waifu.im/random?selected_tags=waifu')
    image_data = response.json()['images'][0]

    image_url = image_data['url']
    source_url = image_data['source']
    color_str = image_data['dominant_color'][1:]
    height = image_data['height']
    width = image_data['width']

    embed = discord.Embed(color=int(color_str[1:], 16))
    embed.description = f'[Source]({source_url}) {width}x{height}'
    embed.set_image(url=image_url)
    embed.set_footer(text='powered by waifu.im')

    await message.channel.send(embed=embed) 


#   # Analyze text and possibly respnod
#   else:
#     try:
#       tone_responses = {
#         'impolite': {
#           'confidence': 0.9,
#           'responses': [
#           "Didn't ask",
#           'Omg pls stfu',
#           'uwu',
#           'L',
#           ]
#         },
#         'frustrated': {
#           'confidence': 0.89,
#           'responses': [
#             'Cool your jets',
#             'Stop harshing the vibe',
#             'Daddy chill',
#             'Calm thy tits',
#             'Mald',
#           ]
#         },
#         'sad': {
#           'confidence': 0.88,
#           'responses': [
#             'Cope',
#             'Cry about it',
#             'Fry about it',
#           ]
#         }
#       }
#       analytics = analyze(message.content)
#       tone = analytics['classifications'][0]
#       if tone['class_name'] in tone_responses and tone['confidence'] > tone_responses[tone['class_name']]['confidence'] and random.random() < 0.2:
#         await message.channel.send(random.choice(tone_responses[tone['class_name']]['responses']))
#       print(analytics['classifications'][:3])
#     except:
#       pass



async def on_raw_message_action(payload):

  # Message is in cache
  if payload.cached_message is not None:

    message = payload.cached_message

    if message.author == bot.user and len(message.components) > 0: return  # Don't save if message has buttons

    if message.author.id == 674785149556097054: return  # Aiden

    kwargs = {}
    if message.author.id == 761148487483785226: kwargs['color'] = 0xcc8899

    # Bot can now snipe its own messages
    # # Stop execution if sender is this bot
    # if message.author == bot.user: return

    # Message has already been deleted recently (in channel)
    if message.channel.id in history and \
    history[message.channel.id][0].is_valid and \
    datetime.datetime.now()-history[message.channel.id][0].deleted_at < SNIPE_DELAY:

      # Put deleted message in queue
      history[message.channel.id].append(Log(message, **kwargs))

    # Sender has not deleted another message recently
    else:

      # Log message normally
      history[message.channel.id] = [Log(message, **kwargs)]


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


# Start clearing memory (recursive thread)
mem_clear()

# Start bot on Discord
bot.run(TOKEN)
