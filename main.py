import discord
from discord.ext import tasks
import os
import random
import time
import tmdbsimple as tmdb
import requests
import asyncio
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

TNG_ID = 655
VOY_ID = 1855
DS9_ID = 580
XFILES_ID = 4087
FRIENDS_ID = 1668
FF_ID = 1437
SIMPSONS_ID = 456


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

TREK_SHOWS = [
  ["TNG", 655, tng_eps],
  ["DS9", 580, ds9_eps]
]

NON_TREK_SHOWS = [
  ["Friends", 1668, friends_eps],
  ["Firefly", 1437, ff_eps],
  ["The Simpsons", 456, simpsons_eps],
  ["Community", 18347, community_eps],
  ["Futurama", 615, futurama_eps],
  ["Buffy the Vampire Slayer", 95, buffy_eps]
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
  random.seed()
  print('We have logged in as {0.user}'.format(client))
  
  
  #episode_quiz.start()
  

@client.event
async def on_message(message):
  global last_message_time, QUIZ_EPISODE, CORRECT_ANSWERS, FUZZ
  
  timestamp = int(time.time())
  difference = int(timestamp - last_message_time)
  random.seed()
 
 
  if message.author == client.user:
    return

  if message.channel.id not in [888090476404674570]:
    return

  if QUIZ_EPISODE:

    threshold = 75

    correct_answer = QUIZ_EPISODE[0].strip().lower()
    
    alt_answer = correct_answer.split()
    stopwords = ["the", "a", "of", "is"]
    resultwords  = [word for word in alt_answer if word.lower() not in stopwords]
    alt_answer = ' '.join(resultwords)

    answers = [correct_answer, alt_answer]
    guess = message.content.lower()
    ratios = list(map(lambda answer: fuzz.ratio(answer, guess), answers))
    pratios = list(map(lambda answer: fuzz.partial_ratio(answer, guess), answers))
    fuzzy_scores = list(map(score_fuzz, zip(ratios, pratios)))
    substring_scores = list(map(lambda answer: score_substring(answer, guess), answers))
    fuzzy_score = max(fuzzy_scores)
    substring_score = max(substring_scores)

    print(list(ratios))
    print(list(substring_scores))
    print(list(fuzzy_scores))
    
    print(fuzzy_score)
    print(substring_score)
    
    award = None
    if substring_score > 0:
      # If there is a precise substring match, don't allow fuzzy score bonus
      award = substring_score
    elif fuzzy_score > 0:
      award = fuzzy_score

    if award:
      id = str(message.author.mention)
      keys = db.keys()
      
      if id in keys:
        points = db[id]
        points += award
        db[id] = points
      else:
        db[id] = award
      if id not in CORRECT_ANSWERS:
          CORRECT_ANSWERS.append(id)
      if id not in FUZZ:
        FUZZ[id] = "Fuzz: " + str(",".join(map(str, ratios)))
        if award == 2:
          FUZZ[id] += " BONUS"
          
      

  if message.content.startswith('!trektalk') and difference <= timeout:
    print("Too fast")
    await message.channel.send("Please give the bot a little more time to cooldown.")
    return

  if message.content.lower() in ["good bot", "nice bot", "fun bot", "sexy bot", "swell bot", "smart bot", "cool bot", "attractive bot", "entertaining bot", "cute bot", "friendly bot", "rad bot", "suave bot"]:
    
    affirmations = ["Thank you!", "Very nice of you to say.", "You're pretty good, yourself!", "`BLUSHING SEQUENCE INITIATED`", "That makes me horny.", "THANKS!!!", "Yay!", "Aw shucks!", "Okay, what do you want?", "Much obliged!", "Subscribe to my OnlyFans!", "Look who's talking :)", "Oh thanks, I'm powered by BLOOD :D", "Oh, stop it, you!", "`COMPLIMENTED ACCEPTED`", "Hands off the merchandise!", "You're welcome!", "Who told you to tell me that?!"]
    await message.channel.send(random.choice(affirmations))

  if message.content.startswith('!faketngtitle'):
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

  if message.content.lower().startswith('!scores') and not QUIZ_EPISODE:
    keys = db.keys()
    scores = []
    msg = "__SCORES__:\n===============\n"
    for c in db.keys():
      un = c.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
      user = await client.fetch_user(un)
      scores.append({"name": user.name, "score" : db[str(c)]})
    scores = sorted(scores, key=lambda k: k['score'], reverse=True)
    for s in scores:
      msg += "`" + s["name"] + ": " + str(s["score"]) + "`" + "\n"
    await message.channel.send(msg)

  
  '''
  if message.content.startswith('!scores'):
    keys = db.keys()
    scoreboard = "Scores:\n"
    i = 1
    for k in keys:
      score = db[k]
      scoreboard += str(k).replace("@", "") + " - " + str(score) + "\n"
      i = i + 1
      if i == 10: 
        break
    await message.channel.send(scoreboard)
    '''


  if message.content.startswith('!trekduel'):
    pick_1 = random.choice(characters)
    pick_2 = random.choice(characters)
    choose_intro = random.choice(war_intros)
    while pick_1 == pick_2:
      pick_2 = random.choice(characters)
    msg = choose_intro + "\n================\n" + message.author.mention + ": Who would win in an arbitrary Star Trek duel?!\n" + "\n> **"+pick_1+"** vs **"+pick_2+"**"
    await message.channel.send(msg)

  if message.content.startswith('!tuvix'):
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
                                    

  if message.content.startswith('!dustbuster'):
    crew = []
    msg = message.author.mention + ", what kind of mission would this Dustbuster club be suited for?  Or are you totally screwed?\n"
    for i in range(5):
      crew.append(random.choice(characters))
    for c in crew:
      msg += "> **"+ c + "**\n"
    await message.channel.send(msg)

  
  if message.content.startswith('!trektalk'):
    last_message_time = int(time.time())
    pick = random.choice(prompts)
    msg =  message.author.mention + "! You want to talk about Trek? Let's talk about Trek! \nPlease answer or talk about the following prompt! One word answers are highly discouraged!\n > **"+pick+"**"
    await message.channel.send(msg)

@tasks.loop(seconds=30,count=1)
async def episode_quiz(non_trek=False):
  global QUIZ_EPISODE
  quiz_channel = client.get_channel(888090476404674570)
  
  headers = {'user-agent': 'Mozilla/5.0'}
  if non_trek:
    print("TV quiz!")
    shows = NON_TREK_SHOWS
  else:
    print("Trek quiz!")
    shows = TREK_SHOWS
  selected_show = random.choice(shows)
  
  show_name = selected_show[0]
  show_id = selected_show[1]
  show_eps = selected_show[2]
  episode = random.choice(show_eps).split("|")
  
  QUIZ_EPISODE = episode
  
  episode_images = tmdb.TV_Episodes(show_id, episode[2], episode[3]).images()
  print("===")
  print(episode_images)
  print("===")
  image = random.choice(episode_images["stills"])
  r = requests.get(TMDB_IMG_PATH + image["file_path"], headers=headers)
  with open('ep.jpg', 'wb') as f:
    f.write(r.content)
  await asyncio.sleep(3)
  await quiz_channel.send(file=discord.File("ep.jpg"))
  await quiz_channel.send("Which episode of __"+str(show_name).upper()+"__ is this?")


@episode_quiz.after_loop
async def quiz_finished():
  global QUIZ_EPISODE, CORRECT_ANSWERS, FUZZ
  await asyncio.sleep(1)
  quiz_channel = client.get_channel(888090476404674570)
  msg = "The episode title was: **{0}** (Season {1} Episode {2})\n".format(QUIZ_EPISODE[0].strip(), QUIZ_EPISODE[2], QUIZ_EPISODE[3])
  if len(CORRECT_ANSWERS) == 0:
    msg += "No one got it this time!"
  else:
    msg += "These people got it:\n"
    for c in CORRECT_ANSWERS:
      points = db[str(c)]
      msg += c + " - Points: **" + str(points) + "**  -  " + FUZZ[str(c)] + "\n"
  await quiz_channel.send(msg)
  CORRECT_ANSWERS = []
  FUZZ = {}
  QUIZ_EPISODE = False
  print("Quiz finished!")


client.run(os.getenv('TOKEN'))
