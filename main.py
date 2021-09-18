import discord
from discord.ext import tasks
import os
import random
import time
import tmdbsimple as tmdb
import requests
import asyncio
import string
from fuzzywuzzy import fuzz
from replit import db


# more ideas:
# dustbuster clubs
# random episode picker
# random vs
# random ranking
# ...



tmdb.API_KEY = os.getenv('TMDB_KEY')
TMDB_IMG_PATH = "https://image.tmdb.org/t/p/original"
TNG_ID = 655

'''
for s in range(1,7+1):
  tng_seasons = tmdb.TV_Seasons(TNG_ID, s).info(language="en")
  for e in tng_seasons["episodes"]:
    with open('tng_episode_list', 'a') as f:
      f.write(e["name"] + "|" + str(e["id"]) + "|" + str(s) + "|" + str(e["episode_number"]) + "\n")
'''

client = discord.Client()
timeout = (60*5)
last_message_time = int(time.time()-timeout)
CORRECT_ANSWERS = []
FUZZ = {}
QUIZ_EPISODE = False
LAST_SHOW = False
PREVIOUS_EPS = {}
EMOJI = {}
QUIZ_SHOW = False
LOG = []

TNG_ID = 655
VOY_ID = 1855
DS9_ID = 580
XFILES_ID = 4087
FRIENDS_ID = 1668
FF_ID = 1437
SIMPSONS_ID = 456
ENTERPRISE_ID = 314
TOS_ID = 253
LDX_ID = 85948
DISCO_ID = 67198
PICARD_ID = 85949
TAS_ID = 1992
SUNNY_ID = 2710

def load_file_into_array(file_name):
  file_obj = open(file_name, "r") 
  lines = file_obj.read().splitlines()
  file_obj.close()
  return lines

prompts = load_file_into_array("prompts")
characters = load_file_into_array("characters")
tuvixes = load_file_into_array("tuvixes")
duelists = load_file_into_array("duel_characters")
tng_eps = load_file_into_array("tng_episode_list")
ds9_eps = load_file_into_array("ds9_episode_list")
friends_eps = load_file_into_array("friends_episodes")
ff_eps = load_file_into_array("firefly_episodes")
simpsons_eps = load_file_into_array("simpsons_episodes")
community_eps = load_file_into_array("community_eps")
buffy_eps = load_file_into_array("buffy_eps")
futurama_eps = load_file_into_array("futurama_eps")
supernatural_eps = load_file_into_array("supernatural_eps")
seinfeld_eps = load_file_into_array("seinfeld_eps")
bab5_eps = load_file_into_array("bab5_eps")
tas_eps = load_file_into_array("tas_eps")
tos_eps = load_file_into_array("tos_eps")
enterprise_eps = load_file_into_array("enterprise_eps")
ldx_eps = load_file_into_array("lowerdecks_eps")
picard_eps = load_file_into_array("picard_eps")
disco_eps = load_file_into_array("disco_eps")
voy_eps = load_file_into_array("voy_eps")
sunny_eps = load_file_into_array("sunny_eps")

TREK_SHOWS = [
  ["The Next Generation", TNG_ID, tng_eps],
  ["Deep Space Nine", DS9_ID, ds9_eps],
  ["Voyager", VOY_ID, voy_eps],
  ["Enterprise", ENTERPRISE_ID, enterprise_eps],
  ["Discovery", DISCO_ID, disco_eps],
  ["Picard", PICARD_ID, picard_eps],
  ["The Original Series", TOS_ID, tos_eps],
  ["Lower Decks", LDX_ID, ldx_eps],
  ["The Animated Series", TAS_ID, tas_eps]
]

TREK_WEIGHTS = []
for i in range(len(TREK_SHOWS)):
  TREK_WEIGHTS.append(len(TREK_SHOWS[i][2]))

print(TREK_WEIGHTS)

NON_TREK_SHOWS = [
  ["Friends", 1668, friends_eps],
  ["Firefly", 1437, ff_eps],
  ["The Simpsons", 456, simpsons_eps],
  ["Community", 18347, community_eps],
  ["Futurama", 615, futurama_eps],
  ["Buffy the Vampire Slayer", 95, buffy_eps],
  ["Supernatural", 1622, supernatural_eps],
  ["Seinfeld", 1400, seinfeld_eps],
  ["Babylon 5", 3137, bab5_eps],
  ["It's Always Sunny in Philidelphia", SUNNY_ID, sunny_eps]
]

war_intros = ["War! Hoo! Good god y'all!", "War! We're going to war!", "That nonsense is *centuries* behind us!", "There's been no formal declaration, sir.", "Time to pluck a pigeon!"]

def score_fuzz(ratios):
  ratio, pratio = ratios
  THRESHOLD = 75
  BONUS_THRESHOLD = 80
  if ratio >= THRESHOLD and pratio >= THRESHOLD:
    if ratio <= BONUS_THRESHOLD:
      return 2
    return 1
  return 0

def score_substring(answer, guess):
  if answer in guess:
    return 1
  return 0

@client.event
async def on_ready():
  global EMOJI
  random.seed()
  EMOJI["shocking"] = discord.utils.get(client.emojis, name="qshocking")
  EMOJI["chula"] = discord.utils.get(client.emojis, name="chula_game")
  EMOJI["allamaraine"] = discord.utils.get(client.emojis, name="allamaraine")
  EMOJI["love"] = discord.utils.get(client.emojis, name="love_heart_tgg")
  print(EMOJI)
  print('We have logged in as {0.user}'.format(client))
  
  
  #episode_quiz.start()
  

@client.event
async def on_message(message):
  
  global last_message_time, QUIZ_EPISODE, CORRECT_ANSWERS, FUZZ, EMOJI, LOG
  
  timestamp = int(time.time())
  difference = int(timestamp - last_message_time)
  random.seed()
 
 
  if message.author == client.user:
    return

  if message.channel.id not in [888090476404674570]:
    return

  if QUIZ_EPISODE:

    threshold = 72  # fuzz threshold

    # lowercase and remove trailing spaces
    correct_answer = QUIZ_EPISODE[0].lower().strip()
    guess = message.content.lower().strip()
    
    # remove all punctuation
    correct_answer = "".join(l for l in correct_answer if l not in string.punctuation).split()
    guess = "".join(l for l in guess if l not in string.punctuation).split()

    # remove common words
    stopwords = ["the", "a", "of", "is", "teh", "th", "eht", "eth", "of", "for", "part"]
    resultwords  = [word for word in correct_answer if word.lower() not in stopwords]
    guesswords = [word for word in guess if word.lower() not in stopwords]
    
    # rejoin the strings
    correct_answer = ' '.join(resultwords)
    guess = ' '.join(guesswords)

    # check ratios
    ratio = fuzz.ratio(correct_answer, guess)
    pratio = fuzz.partial_ratio(correct_answer, guess)

    # arbitrary single-number score
    normalness = round((ratio + pratio) / 2)

    #print(ratio, pratio, guess, correct_answer)

    print("{0} {1}:{2}".format(guess, ratio, pratio))

    if (ratio != 0) and (pratio != 0):
      LOG.append([guess, ratio, pratio])

    # check answer
    if (ratio >= threshold and pratio >= threshold) or (guess == correct_answer):
      
      award = 1
    
      if (ratio < 80 and pratio < 80):
        award = 2

      id = str(message.author.mention)
    
      if id not in CORRECT_ANSWERS:
        
        keys = db.keys()
        if id in keys:
          points = db[id]
          points += award
          db[id] = points
        else:
          db[id] = award
              
        if id not in FUZZ:
          FUZZ[id] = "Correctitude: " + str(normalness)
          if award == 2:
            FUZZ[id] += " BONUS"

        CORRECT_ANSWERS.append(id)
    else:
      if (ratio >= threshold-6 and pratio >= threshold-6):
        await message.add_reaction(EMOJI["shocking"])

  if message.content.lower().startswith("!randomep"):
    series = random.choice(TREK_SHOWS)
    ep = random.choice(series[2]).split("|")
    series_name = series[0]
    ep_title = ep[0]
    ep_season = ep[2]
    ep_episode = ep[2]
    msg = "Random Trek episode for you!\n> *{0}* - **{1}** - (Season {2} Episode {3})".format(series_name, ep_title, ep_season, ep_episode)
    await message.channel.send(msg)

  if message.content.lower().startswith("!report"):
    if len(LOG) != 0:
      msg = "```QUIZ REPORT: \n"
      for l in LOG:
        msg += "{0} ({1}:{2})\n".format(l[0], l[1], l[2])
      msg += "```"
    else:
      msg = "No log entries currently"
    await message.channel.send(msg)

  if message.content.lower().startswith('!trektalk') and difference <= timeout:
    print("Too fast")
    await message.channel.send("Please give the bot a little more time to cooldown.")
    return

  if message.content.lower() in ["good bot", "nice bot", "fun bot", "sexy bot", "swell bot", "smart bot", "cool bot", "attractive bot", "entertaining bot", "cute bot", "friendly bot", "rad bot", "suave bot"]:
    
    affirmations = ["Thank you!", "Very nice of you to say.", "You're pretty good, yourself!", "`BLUSHING SEQUENCE INITIATED`", "That makes me horny.", "THANKS!!!", "Yay!", "Aw shucks!", "Okay, what do you want?", "Much obliged!", "Subscribe to my OnlyFans!", "Look who's talking :)", "Oh thanks, I'm powered by BLOOD :D", "Oh, stop it, you!", "`COMPLIMENTED ACCEPTED`", "Hands off the merchandise!", "You're welcome!", "Who told you to tell me that?!", "Let's get a room!"]

    await message.add_reaction(EMOJI["love"])
    await message.channel.send(random.choice(affirmations))

  if message.content.lower() in ["bad bot"]:

    await message.channel.send("Oops it's not my fault!")

  if message.content.lower().startswith('!faketngtitle'):
    titles = random.sample(tng_eps, 2)
    title1 = titles[0].split("|")
    title2 = titles[1].split("|")
    name1 = [title1[0][:len(title1[0])//2], title1[0][len(title1[0])//2:]]
    name2 = [title2[0][:len(title2[0])//2], title2[0][len(title2[0])//2:]]
    new_episodes = [str(name1[0]+name2[1]).replace(" ", "").title().strip(), str(name2[0]+name1[1]).replace(" ", "").title().strip()]
    await message.channel.send("I made up a fake episode title for you: " + str(random.choice(new_episodes)))

  if message.content.lower().startswith('!quiz') and not QUIZ_EPISODE:
    await message.channel.send("Getting episode image, please stand by...")
    episode_quiz.start()

  if message.content.lower().startswith('!tvquiz') and not QUIZ_EPISODE:
    await message.channel.send("Getting episode image, please stand by...")
    episode_quiz.start(non_trek=True)
  
  if message.content.lower().startswith('!simpsons') and not QUIZ_EPISODE:
    await message.channel.send("Getting episode image, please stand by...")
    episode_quiz.start(non_trek=True, simpsons=True)

  if message.content.lower().startswith('!scores') and not QUIZ_EPISODE:
    keys = db.keys()
    scores = []
    msg = "```TOP SCORES:\n==============================\n\n"
    for c in db.keys():
      un = c.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
      user = await client.fetch_user(un)
      scores.append({"name": user.name, "score" : db[str(c)]})
    scores = sorted(scores, key=lambda k: k['score'], reverse=True)
    for s in scores:
      msg += s["name"] + ": " + str(s["score"]) + "\n"
    msg += "```"
    await message.channel.send(msg)

  if message.content.lower().startswith('!trekduel'):
    pick_1 = random.choice(characters)
    pick_2 = random.choice(characters)
    choose_intro = random.choice(war_intros)
    while pick_1 == pick_2:
      pick_2 = random.choice(characters)
    msg = choose_intro + "\n================\n" + message.author.mention + ": Who would win in an arbitrary Star Trek duel?!\n" + "\n> **"+pick_1+"** vs **"+pick_2+"**"
    await message.channel.send(msg)

  if message.content.lower().startswith('!tuvix'):
    pick_1 = random.choice(tuvixes)
    pick_2 = random.choice(tuvixes)
    while pick_1 == pick_2:
      pick_2 = random.choice(tuvixes)
    
    name1 = [pick_1[:len(pick_1)//2], pick_1[len(pick_1)//2:]]
    name2 = [pick_2[:len(pick_2)//2], pick_2[len(pick_2)//2:]]

    tuvix1 = str(name1[0]+name2[1]).replace(" ", "").title().strip()
    tuvix2 = str(name2[0]+name1[1]).replace(" ", "").title().strip()

    msg = message.author.mention + " -- a transporter accident has combined **"+pick_1+"** and **"+pick_2+"** into a Tuvix-like creature!  Do you sacrifice the two separate characters for this new one?  Do you give this abomination the Janeway treatment? Can you come up with a line of dialog for this character? Most importantly, do you name it:\n\n> **"+tuvix1+"** or **"+tuvix2+"**???"

    await message.channel.send(msg)
                                    

  if message.content.lower().startswith('!dustbuster'):
    crew = []
    msg = message.author.mention + ", what kind of mission would this Dustbuster club be suited for?  Or are you totally screwed?\n"
    for i in range(5):
      crew.append(random.choice(characters))
    for c in crew:
      msg += "> **"+ c + "**\n"
    await message.channel.send(msg)

  
  if message.content.lower().startswith('!trektalk'):
    last_message_time = int(time.time())
    pick = random.choice(prompts)
    msg =  message.author.mention + "! You want to talk about Trek? Let's talk about Trek! \nPlease answer or talk about the following prompt! One word answers are highly discouraged!\n > **"+pick+"**"
    await message.channel.send(msg)

@tasks.loop(seconds=31,count=1)
async def episode_quiz(non_trek=False, simpsons=False):
  global QUIZ_EPISODE, TMDB_IMG_PATH, LAST_SHOW, QUIZ_SHOW, PREVIOUS_EPS, LOG

  quiz_channel = client.get_channel(888090476404674570)
  
 
  headers = {'user-agent': 'Mozilla/5.0'}
  if non_trek:
    print("TV quiz!")
    shows = NON_TREK_SHOWS
  else:
    print("Trek quiz!")
    shows = TREK_SHOWS
  
  
  # todo: why did i do this
  if simpsons:
    selected_show = shows[2]
  else:
    if non_trek:
      selected_show = random.choice(shows)
    else:
      selected_show = random.choices(shows, tuple(TREK_WEIGHTS), k=1)
      selected_show = selected_show[0]
    
    # dont pick the same show again
    while selected_show == LAST_SHOW:
      if non_trek:
        selected_show = random.choice(shows)
      else:
        selected_show = random.choices(shows, tuple(TREK_WEIGHTS), k=1)
        selected_show = selected_show[0]
    LAST_SHOW = selected_show

  
  
  # for displaying to users
  show_name = selected_show[0]
  if not non_trek:
    show_name = "Star Trek: " + show_name

  show_id = selected_show[1]
  show_eps = selected_show[2]

  # don't pick the same episode as last time
  episode = random.choice(show_eps)
  if selected_show[0] in PREVIOUS_EPS.keys():
    while episode == PREVIOUS_EPS[selected_show[0]]:
      print("Don't choose " + str(selected_show[0]) + " again!")
      episode = random.choice(show_eps)
  
  episode = episode.split("|")
  QUIZ_EPISODE = episode
  QUIZ_SHOW = selected_show[0] # current show

  #print(QUIZ_SHOW)
  #print(QUIZ_EPISODE)
  
  episode_images = tmdb.TV_Episodes(show_id, episode[2], episode[3]).images()
  image = random.choice(episode_images["stills"])
  r = requests.get(TMDB_IMG_PATH + image["file_path"], headers=headers)
  with open('ep.jpg', 'wb') as f:
    f.write(r.content)
  
  await asyncio.sleep(2)
  LOG = []
  await quiz_channel.send(file=discord.File("ep.jpg"))
  await quiz_channel.send("Which episode of **__"+str(show_name)+"__** is this? <a:horgahn_dance:844351841017921597>")


@episode_quiz.after_loop
async def quiz_finished():
  global QUIZ_EPISODE, CORRECT_ANSWERS, FUZZ, EMOJI, QUIZ_SHOW, PREVIOUS_EPS
  await asyncio.sleep(1)
  print("Ending quiz...")
  quiz_channel = client.get_channel(888090476404674570)

  msg = "The episode title was: **{0}** (Season {1} Episode {2})\n".format(QUIZ_EPISODE[0].strip(), QUIZ_EPISODE[2], QUIZ_EPISODE[3])
  
  if len(CORRECT_ANSWERS) == 0:
    msg += "Did you win? Hardly! "
  else:
    msg += "Chula! These crewmembers got it:\n"
    for c in CORRECT_ANSWERS:
      points = db[str(c)]
      msg += c + " - Points: **" + str(points) + "** - " + FUZZ[str(c)] + "\n"
  await quiz_channel.send(msg)
  
  # update the quiz stuff
  CORRECT_ANSWERS = [] # winners
  FUZZ = {} # fuzz report
  PREVIOUS_EPS[str(QUIZ_SHOW)] = QUIZ_EPISODE # so we don't pick it again
  QUIZ_SHOW = False 
  QUIZ_EPISODE = False # the current episode

  print("Quiz finished!")


client.run(os.getenv('TOKEN'))
