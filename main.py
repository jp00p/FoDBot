import discord
from discord.ext import tasks
import os
import random
import time
import tmdbsimple as tmdb
import requests
import asyncio
import string
from PIL import Image
from fuzzywuzzy import fuzz
from replit import db


tmdb.API_KEY = os.getenv('TMDB_KEY')
TMDB_IMG_PATH = "https://image.tmdb.org/t/p/original"
TNG_ID = 655

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
SLOTS_RUNNING = False

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

SLOTS =  {
    "TNG" : {
      "files" : "./slots/tng/",
      "payout" : 1,
      "matches" : {
        "villains" : ["armus", "pakled", "lore"],
        "federation captains" : ["picard", "jellico"],
        "olds" : ["pulaski", "jellico", "picard", "kevin"],
        "no law to fit your crime" : ["picard", "kevin"],
        "music box torture" : ["kevin", "troi"],
        "ensigns" : ["ro", "wesley"],
        "omnipotent" : ["q", "armus", "kevin"],
        "brothers" : ["data", "lore"],
        "doctors" : ["beverly", "pulaski"],
        "drunks" : ["obrien", "pulaski"],
        "rascals" : ["ro", "guinan", "picard", "keiko"],
        "aliens" : ["armus", "guinan", "pakled", "q", "worf", "troi", "ro", "kevin"],
        "baby delivery team" : ["worf", "keiko"],
        "robot fuck team" : ["data", "yar"],
        "loving couple" : ["obrien", "keiko"],
        "best friends" : ["geordi", "data"],
        "jazz funeral" : ["geordi", "ro"],
        "engineers" : ["geordi", "obrien"],
        "nexus travellers" : ["guinan", "picard"],
        "related to jack crusher" : ["beverly", "wesley"],
        "eggs for breakfast" : ["riker", "pulaski", "worf"],
        "humanity on trial" : ["q", "picard"],
        "delta shift" : ["riker", "jellico"],
        "imzadi" : ["troi", "riker"],
        "nice house, good tea" : ["worf", "kevin"],
        "empty death" : ["yar", "armus"],
        "butting heads" : ["riker", "ro"],
        "leotard buddies" : ["beverly", "troi"],
        "security squad" : ["worf", "yar"],
        "coffee and croissants" : ["picard", "beverly"],
        "uncomfortable with children" : ["picard", "wesley"],
        "bean flicking stance" : ["guinan", "q"],
        "i dont need your fantasy women" : ["riker", "q"]
      }
    },
    "DS9" : {
      "files" : "./slots/ds9/",
      "payout" : 1.5,
      "matches": {
        "the dominion" : ["weyoun4", "weyoun5", "weyoun6", "yelgrun", "keevan", "kilana", "flakeleader", "goranagar", "ikatika"],
        "\"old man\"" : ["jadzia", "sisko"],
        "slug buddies" : ["ezri", "jadzia"],
        "bajoran spiritual leaders" : ["bareil", "opaka", "winn", "sisko"],
        "siskos lovers" : ["jennifer", "kasidy"],
        "love is blind" : ["winn", "dukat"],
        "lunch date" : ["bashir", "garak"],
        "holodeck date" : ["bashir", "obrien"],
        "villains" : ["winn", "dukat", "flakeleader"],
        "jeffreys" : ["weyoun4", "weyoun5", "weyoun6", "brunt"],
        "enterprise officers" : ["worf", "obrien"],
        "bell rioters" : ["sisko", "bashir", "jadzia"],
        "promenade hangin'" : ["jake", "nog"],
        "golden liquid" : ["bashir", "odo", "flakeleader"],
        "voorta" : ["weyoun4", "weyoun5", "weyoun6", "yelgrun", "keevan", "kilana"],
        "secret societies" : ["sloan", "garak", "flakeleader"],
        "search for the cure" : ["bashir", "goranagar"],
        "violent love" : ["worf", "jadzia"],
        "dance in my golden sparkles" : ["odo", "kira"],
        "niners" : ["sisko", "worf", "rom", "ezri", "kira", "bashir", "nog", "quark"],
        "take me out to the ballgame" : ["sisko", "bokai"],
        "not real" : ["bokai", "vic"],
        "breaking the ferengi mold" : ["rom", "nog", "ishka"],
        "naguses" : ["brunt", "zek", "rom", "quark"],
        "affectionate touches" : ["jake", "sisko"],
        "drinking buddies" : ["gowron", "jadzia"],
        "love conquers mountains" : ["quark", "odo"],
        "did he fuck her mom?" : ["kira", "dukat"],
        "cardassians" : ["dukat", "garak"],
        "piano lessons" : ["vic", "odo"],
        "lounge lizard" : ["vic", "nog"],
        "who?" : ["goranagar", "ikatika", "yelgrun", "keevan"],
        "possible changeling spy" : ["gowron", "bashir"],
        "prison pals" : ["obrien", "ezri", "martok", "bashir", "garak"],
        "battled the pahwraiths" : ["winn", "jake", "sisko", "obrien"],
        "senator killers" : ["garak", "sisko"],
        "engineers" : ["obrien", "rom"],
        "starfleet intelligence" : ["obrien", "bashir", "sloan"],
        "probably unmodified humans" : ["jake", "jennifer", "sisko", "obrien"],
        "smugglers" : ["quark", "kasidy"],
        "quark haters" : ["kira", "brunt", "odo"],
        "rsvp" : ["jennifer", "jadzia", "bareil", "winn", "dukat", "weyoun4", "weyoun5", "weyoun6", "keevan", "sloan"],
        "profitable lovers" : ["ishka", "zek"]
      }
    },
    "TEST" : {
      "files" : "./slots/test/",
      "matches" : {
        "armus" : ["armus"]
      }
    }
}

# SLOTS["TNG"]["files"]





def load_file_into_array(file_name):
  file_obj = open(file_name, "r") 
  lines = file_obj.read().splitlines()
  file_obj.close()
  return lines

prompts = load_file_into_array("prompts")
characters = load_file_into_array("characters")
fmk_characters = load_file_into_array("fmk_chars")
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

#print(TREK_WEIGHTS)

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

@client.event
async def on_ready():
  global EMOJI
  random.seed()
  EMOJI["shocking"] = discord.utils.get(client.emojis, name="qshocking")
  EMOJI["chula"] = discord.utils.get(client.emojis, name="chula_game")
  EMOJI["allamaraine"] = discord.utils.get(client.emojis, name="allamaraine")
  EMOJI["love"] = discord.utils.get(client.emojis, name="love_heart_tgg")
  #print(EMOJI)
  keys = db.keys()
  if "jackpot" not in keys:
    db["jackpot"] = 0
  if "jackpots" not in keys:
    db["jackpots"] = []
  print('We have logged in as {0.user}'.format(client))
  

@client.event
async def on_message(message):
  
  global last_message_time, QUIZ_EPISODE, CORRECT_ANSWERS, FUZZ, EMOJI, LOG, SLOTS_RUNNING
  
  SLOTS_CHANNEL = 891412391026360320
  QUIZ_CHANNEL = 891412585646268486
  CONVO_CHANNEL = 891412924193726465

  timestamp = int(time.time())
  difference = int(timestamp - last_message_time)
  random.seed()
 
 
  if message.author == client.user:
    return

  if message.channel.id not in [888090476404674570, SLOTS_CHANNEL, QUIZ_CHANNEL, CONVO_CHANNEL]:
    return

  # register player if need be
  register_player(message.author)
  

  if QUIZ_EPISODE and message.channel.id == QUIZ_CHANNEL:

    threshold = 72  # fuzz threshold

    # lowercase and remove trailing spaces
    correct_answer = QUIZ_EPISODE[0].lower().strip()
    guess = message.content.lower().strip()
    
    # remove all punctuation
    correct_answer = "".join(l for l in correct_answer if l not in string.punctuation).split()
    guess = "".join(l for l in guess if l not in string.punctuation).split()

    # remove common words
    stopwords = ["the", "a", "of", "is", "teh", "th", "eht", "eth", "of", "for", "part 1", "part 2", "in", "are", "an", "as", "and"]
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

    #print("{0} {1}:{2}".format(guess, ratio, pratio))

    if (ratio != 0) and (pratio != 0):
      LOG.append([guess, ratio, pratio])

    # check answer
    if (ratio >= threshold and pratio >= threshold) or (guess == correct_answer):
      
      # correct answer      
      award = 1
    
      if (ratio < 80 and pratio < 80):
        award = 2
     
      id = str(message.author.id) # new db stuff
      if id not in CORRECT_ANSWERS:
        player = db[id].value
        if not CORRECT_ANSWERS:
          player["score"] += award * 10
        else:
          player["score"] += award
        db[id] = player


        if id not in FUZZ:
          score_str = "`Correctitude: " + str(normalness) +"`"
          if award == 1:
            score_str += " <:combadge:867891664886562816>"
          else:
            score_str += " <a:combadge_spin:867891818317873192>"
          FUZZ[id] = score_str

        CORRECT_ANSWERS.append(id)
    else:
      if (ratio >= threshold-6 and pratio >= threshold-6):
        await message.add_reaction(EMOJI["shocking"])





  if message.content.lower().startswith("!help"):
    msg = '''

__GAME COMMANDS:__
`!slot` or `!slot ds9` - run the slot machine!
`!setwager 1` - set your default wager to 1 (try a different number!)
`!quiz` - run a Trek quiz!
`!tvquiz` - run a non-Trek quiz!
`!simpsons` - run a Simpsons quiz!
`!scores` - list the current scores
`!jackpot` - show the current jackpot
`!report` - show the fuzz report for the last quiz

__TREK COMMANDS:__
`!tuvix` - create your own Tuvix
`!dustbuster` - beam em down, let god sort em out
`!randomep` - pick a random episode from all trek everywhere
`!trektalk` - generate a conversation piece
`!trekduel` - double-axe-handle your friends
`!fmk` - you know the deal

__SLOTS INFO:__
TNG slots have a jackpot payout of `1x`
DS9 slots have a jackpot payout of `1.5x`
You get a jackpot if you get all 3 characters the same!

__QUIZ INFO:__
Episode quizzes do not have to be a perfect match.
In fact, you get bonus points for being just wrong enough.
You need to get your fuzziness between 72 and 80 for the bonus.
First person to get it right (or wrong enough) will get their score multiplied by 10!
Run the `!report` to see the details after a quiz!

Report any fucked up bot behavior to jp00p!
'''
    await message.channel.send(msg)




  if message.channel.id == SLOTS_CHANNEL and message.content.lower().startswith("!testslots"):
    
    if message.author.id == 572540272563716116:

      if message.content.lower().replace("!testslots ", "") == "ds9":
        roll = "DS9"
      else:
        roll = "TNG"

      spins = 100000
      spin_msg = f"Testing {roll} slots with {spins} spins! Nothing is going to work until this finishes sorry :)"

      await message.channel.send(spin_msg)

      jackpots = 0
      wins = 0
      profitable_wins = 0
      profits = []
      for i in range(spins):
        
        silly,clones,jackpot = roll_slot(roll, generate_image=False)
        profit = len(silly)
        if len(silly) > 0 or len(clones) > 0:
          wins += 1
        if len(silly) > 1 or len(clones) > 0:
          profitable_wins += 1
        if len(clones) > 0:
          profit += 3
        if jackpot:
          jackpots += 1
        profits.append(profit)
        

      chance_to_win = (wins/spins)*100
      chance_to_jackpot = (jackpots/spins)*100
      chance_for_profit = (profitable_wins/spins)*100
      average_profit = sum(profits) / len(profits)

      msg = "\nOut of {0} test spins, there were a total of {1} wins, {2} of those wins being jackpots.\nAverage chance of winning per spin: {3}%.\nAverage chance of jackpot per spin: {4}%.\nNumber of profitable spins: {5}\nChance for profit: {6}%\nAverage profit per spin: {7} points (not counting jackpots)".format(spins,wins,jackpots, chance_to_win, chance_to_jackpot, profitable_wins, chance_for_profit, average_profit)

      await message.channel.send(msg)

    else:

      await message.channel.send("ah ah ah, you didn't say the magic word")


    
  if message.channel.id == SLOTS_CHANNEL and message.content.lower().startswith("!jackpots"):
    all_jackpots = db["jackpots"].value

    if all_jackpots:
      all_jackpots.reverse()
      msg = "Previous jackpot winners:\n"
      for j in all_jackpots:
        msg += "{0}: {1}\n".format(j[1], j[0])
      await message.channel.send(msg)
    else:
      await message.channel.send("Jackpot DB is currently empty!")
      


  if message.channel.id == SLOTS_CHANNEL and message.content.lower().startswith("!slots"):
    
    if message.content.lower().replace("!slots ", "") == "ds9":
      roll = "DS9"
    else:
      roll = "TNG"

    if SLOTS_RUNNING:
      # dont run again while slots are processing
      await message.channel.send("Hold up! This bot isn't good at multitasking!")
    
    else:
      free_spin = True
      id = str(message.author.id)
      player = db[id].value
      free_spin = True

      if "spins" in player:
        # not all players have spins
        if player["spins"] >= 3:
          free_spin = False
      else:
        player["spins"] = 0
      
      wager = 1
      if "wager" in player:
        wager = player["wager"]
      

      if player["score"] < wager and not free_spin:
        await message.channel.send(f"You need at least {wager} point(s) to spin! (Play the quiz to get more points or try changing your wager")
      else:
        if not free_spin:
          player["score"] -= wager

        
        # don't increment a freshly initialized spin
        player["spins"] += 1
        
        spinnin = ["All I do is *slots slots slots*!", "Time to pluck a pigeon!", "Rollin' with my homies...", "It's time to spin!", "Let's roll.", "ROLL OUT!", "Get it player.", "Go go gadget slots!", "Activating slot subroutines!", "Reversing polarity on Alpha-probability particle emitters."]
        
        spin_msg = message.author.mention + ": "
        spin_msg += random.choice(spinnin)

        if free_spin:
          spin_msg += " **This one's on the house!** (after 3 free spins, they will cost you points!)"
        else:
          spin_msg += f" Spending `{wager}` of your points!"

        spin_msg += " This is spin #{0} for you.".format(player["spins"])

        db[id] = player # update player
        await message.channel.send(spin_msg)
      
        payout = SLOTS[roll]["payout"]

        # roll the slots!
        silly_matches, matching_chars, jackpot = roll_slot(roll, filename=str(message.author.id))
      
        rewards = 0

        #print(silly_matches, matching_chars, jackpot)
        #await message.channel.send(file=discord.File("./slot_results/"+str(message.author.id)+".png"))
      
        match_msg = message.author.mention + "'s spin results: \n"
        
        if len(silly_matches) > 0:
          match_msg += "**Matches: ** "
          match_msg += "; ".join(silly_matches).title()
          match_msg += " `" + str(len(silly_matches)*wager) + " point(s)`\n"
          rewards += len(silly_matches) * wager
          
        if len(matching_chars) > 0:
          match_msg += "**Transporter clones: ** "
          match_msg += ", ".join(matching_chars).title()
          match_msg += " `({0} points)`\n".format(3 * wager)
          rewards += 3 * wager

        if jackpot:

          amt = db["jackpot"]
          total_amt = round(amt * payout)
          #bonus = (total_amt - amt)
          jackpot_data = [total_amt, message.author.name]
          all_jackpots = db["jackpots"]
          all_jackpots.append(jackpot_data)
          db["jackpots"] = all_jackpots
          jackpot_art = '''
 .     *        .    *       ________________ _      .    ____      *
     *     .       .     .  <-_______________|*) .  ___==/    \==___
                     . *     ~.      *   | |  ~  --==================--
    J A C K P O T !!!    .      .      . | |  *  /  ^/  --=====--
    .     .     .         .        ______|_|____/___/     .        .
  .   *  .       *   .      ()   . ==__        ....^T/_      .
      .      .      .*      .    .  *  --___________|\~  .     *.    .
  .              .        .   *    .            .        *     .
'''
          match_msg += "```" + jackpot_art + "```"
          match_msg += "\n> @here "+message.author.mention+" wins the pot of: {0} multiplied by the slots' jackpot payout rate of {1} -- for a total winnings of {2}\n========================\nJackpot has been reset to: **100** \n".format(db["jackpot"], payout, total_amt)
          rewards += db["jackpot"]
          db["jackpot"] = 100 # reset the jackpot

        if rewards != 0:
          player["score"] += rewards
          if free_spin:
            rewards += wager
          match_msg += "**Total Profit:** `{0} point(s)`.  Your score is now: `{1}`\n".format(rewards-wager, player["score"])
          db[id] = player
          
          embed = discord.Embed(
            title="Results",
            color=discord.Color(0x1abc9c),
            description=match_msg,
          )

          file = discord.File("./slot_results/{0}.png".format(message.author.id), filename=str(message.author.id)+".png")
          embed.set_image(url="attachment://{0}.png".format(message.author.id))

          await message.channel.send(embed=embed, file=file)
        else:
          
          
          db["jackpot"] += wager
          
          loser = ["No dice!", "Bust!", "No matches!", "Better luck next time!", "Sad trombone!", "You didn't win!", "We have no prize to fit your loss -- ", "You may have won in the mirror universe, but not here!", "Sensors detect no matches.", "JACKP-- no wait, that's a loss.", "Close, but no cigar.", "Not a win!", "You would have won if it were opposite day!"]

          embed = discord.Embed(
            title="Results",
            color=discord.Color(0xe74c3c),
            description="{0}: {1} {2} point(s) added to the jackpot, increasing it's bounty to `{3}`. Your score is now: `{4}`".format(message.author.mention, random.choice(loser), wager, db["jackpot"], player["score"]),
          )
          
          await message.channel.send(embed=embed)

        SLOTS_RUNNING = False


  if message.channel.id == SLOTS_CHANNEL and message.content.lower().startswith("!setwager"):
    player = db[str(message.author.id)].value
    min_wager = 1
    max_wager = 100000
    wager_val = message.content.lower().replace("!setwager ", "")


    if wager_val.isnumeric():
      wager_val = int(wager_val)
      if wager_val >= min_wager and wager_val <= max_wager:
        player["wager"] = int(wager_val)
        msg = f"Your default wager has been set to {wager_val}"
        db[str(message.author.id)] = player
        await message.channel.send(msg)
      else:
        msg = f"Wager must be a number between `{min_wager}` and `{max_wager}`"
        await message.channel.send(msg)
    else:
      msg = f"Wager must be a number between `{min_wager}` and `{max_wager}`"
      await message.channel.send(msg)
    


  if message.channel.id == CONVO_CHANNEL and message.content.lower().startswith("!randomep"):
    series = random.choice(TREK_SHOWS)
    ep = random.choice(series[2]).split("|")
    series_name = series[0]
    ep_title = ep[0]
    ep_season = ep[2]
    ep_episode = ep[3]
    msg = "Random Trek episode for you!\n> *{0}* - **{1}** - (Season {2} Episode {3})".format(series_name, ep_title, ep_season, ep_episode)
    await message.channel.send(msg)  







  if message.channel.id == QUIZ_CHANNEL and message.content.lower().startswith("!report"):
    if len(LOG) != 0:
      msg = "```QUIZ REPORT: \n"
      for l in LOG:
        msg += "{0} ({1}:{2})\n".format(l[0], l[1], l[2])
      msg += "```"
    else:
      msg = "No log entries currently"
    await message.channel.send(msg)



  if message.content.lower() in ["good bot", "nice bot", "fun bot", "sexy bot", "swell bot", "smart bot", "cool bot", "attractive bot", "entertaining bot", "cute bot", "friendly bot", "rad bot", "suave bot"]:
    
    affirmations = ["Thank you!", "Very nice of you to say.", "You're pretty good, yourself!", "`BLUSHING SEQUENCE INITIATED`", "That makes me horny.", "THANKS!!!", "Yay!", "Aw shucks!", "Okay, what do you want?", "Much obliged!", "Subscribe to my OnlyFans!", "Look who's talking :)", "Oh thanks, I'm powered by BLOOD :D", "Oh, stop it, you!", "`COMPLIMENTED ACCEPTED`", "Hands off the merchandise!", "You're welcome!", "Who told you to tell me that?!", "Let's get a room!"]

    await message.add_reaction(EMOJI["love"])
    await message.channel.send(random.choice(affirmations))

  if message.content.lower() in ["bad bot"]:
    await message.channel.send("Oops it's not my fault! Blame jp00p!")



  if message.channel.id == CONVO_CHANNEL and message.content.lower().startswith('!trektalk') and difference <= timeout:
    print("Too fast")
    await message.channel.send("Please give the bot a little more time to cooldown.")
    return

  if message.channel.id == CONVO_CHANNEL and message.content.lower().startswith('!faketngtitle'):
    titles = random.sample(tng_eps, 2)
    title1 = titles[0].split("|")
    title2 = titles[1].split("|")
    name1 = [title1[0][:len(title1[0])//2], title1[0][len(title1[0])//2:]]
    name2 = [title2[0][:len(title2[0])//2], title2[0][len(title2[0])//2:]]
    new_episodes = [str(name1[0]+name2[1]).replace(" ", "").title().strip(), str(name2[0]+name1[1]).replace(" ", "").title().strip()]
    await message.channel.send("I made up a fake episode title for you: " + str(random.choice(new_episodes)))

  if message.channel.id == QUIZ_CHANNEL and message.content.lower().startswith('!quiz') and not QUIZ_EPISODE:
    await message.channel.send("Getting episode image, please stand by...")
    episode_quiz.start()

  if message.channel.id == SLOTS_CHANNEL and message.content.lower().startswith('!jackpot'):
    await message.channel.send("Current jackpot bounty is: {0}".format(db["jackpot"]))

  if message.channel.id == QUIZ_CHANNEL and message.content.lower().startswith('!tvquiz') and not QUIZ_EPISODE:
    await message.channel.send("Getting episode image, please stand by...")
    episode_quiz.start(non_trek=True)
  
  if message.channel.id == QUIZ_CHANNEL and message.content.lower().startswith('!simpsons') and not QUIZ_EPISODE:
    await message.channel.send("Getting episode image, please stand by...")
    episode_quiz.start(non_trek=True, simpsons=True)

  if message.content.lower().startswith('!scores'):

    scores = []
    msg = "```TOP SCORES:\n==============================\n\n"
    total_spins = 0
    for c in db.keys():
      if c.isnumeric():
        player = db[str(c)]
        spins = 0
        if "spins" in player:
          spins = player["spins"]
          total_spins += spins
        #un = c.replace("@", "").replace("<", "").replace(">", "").replace("!", "")
        scores.append({"name": player["name"], "score" : player["score"], "spins" : spins })
    
    scores = sorted(scores, key=lambda k: k['score'], reverse=True)
    for s in scores:
      msg += "{1} - {0} [Spins: {2}]\n".format(s["name"], s["score"], s["spins"])
    msg += "\nTOTAL SPINS: {0}".format(total_spins)
    msg += "```"
    await message.channel.send(msg)

  if message.channel.id == CONVO_CHANNEL and message.content.lower().startswith('!trekduel'):
    pick_1 = random.choice(characters)
    pick_2 = random.choice(characters)
    choose_intro = random.choice(war_intros)
    while pick_1 == pick_2:
      pick_2 = random.choice(characters)
    msg = choose_intro + "\n================\n" + message.author.mention + ": Who would win in an arbitrary Star Trek duel?!\n" + "\n> **"+pick_1+"** vs **"+pick_2+"**"
    await message.channel.send(msg)

  if message.channel.id == CONVO_CHANNEL and message.content.lower().startswith('!tuvix'):
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


  if message.channel.id == CONVO_CHANNEL and message.content.lower().startswith("!fmk"):
    choices = random.sample(fmk_characters, k=3)
    msg = message.author.mention + ": Fuck Marry Kill (or Kiss) -- \n**{}, {}, {}**".format(choices[0], choices[1], choices[2])
    await message.channel.send(msg)


  if message.channel.id == CONVO_CHANNEL and message.content.lower().startswith('!dustbuster'):
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


  await client.change_presence(activity=discord.Game("Current Jackpot: {}".format(db["jackpot"]), type=3))

@tasks.loop(seconds=31,count=1)
async def episode_quiz(non_trek=False, simpsons=False):
  global QUIZ_EPISODE, TMDB_IMG_PATH, LAST_SHOW, QUIZ_SHOW, PREVIOUS_EPS, LOG

  quiz_channel = client.get_channel(891412585646268486)
  
 
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
      episode = random.choice(show_eps)
  PREVIOUS_EPS[selected_show[0]] = episode
  
  episode = episode.split("|")
  QUIZ_EPISODE = episode
  QUIZ_SHOW = selected_show[0] # current show

  episode_images = tmdb.TV_Episodes(show_id, episode[2], episode[3]).images()
  image = random.choice(episode_images["stills"])
  r = requests.get(TMDB_IMG_PATH + image["file_path"], headers=headers)
  with open('ep.jpg', 'wb') as f:
    f.write(r.content)
  
  await asyncio.sleep(2)
  LOG = [] # reset the log
  await quiz_channel.send(file=discord.File("ep.jpg"))
  await quiz_channel.send("Which episode of **__"+str(show_name)+"__** is this? <a:horgahn_dance:844351841017921597>")


@episode_quiz.after_loop
async def quiz_finished():
  global QUIZ_EPISODE, CORRECT_ANSWERS, FUZZ, EMOJI, QUIZ_SHOW, PREVIOUS_EPS
  await asyncio.sleep(1)
  print("Ending quiz...")
  quiz_channel = client.get_channel(891412585646268486)

  msg = "The episode title was: **{0}** (Season {1} Episode {2})\n".format(QUIZ_EPISODE[0].strip(), QUIZ_EPISODE[2], QUIZ_EPISODE[3])
  
  if len(CORRECT_ANSWERS) == 0:
    msg += "Did you win? Hardly! Adding a point to the slots jackpot."
    db["jackpot"] += 1
  else:
    msg += "Chula! These crewmembers got it:\n"
    for c in CORRECT_ANSWERS:
      player = db[str(c)].value
      msg += player["mention"] + " - Points: **" + str(player["score"]) + "** - " + FUZZ[str(c)] + "\n"
  await quiz_channel.send(msg)
  
  # update the quiz stuff
  CORRECT_ANSWERS = [] # winners
  FUZZ = {} # fuzz report
  QUIZ_SHOW = False 
  QUIZ_EPISODE = False # the current episode

  print("Quiz finished!")



def roll_slot(slot_series, generate_image=True, filename="slot_results.png"):
  global SLOTS, SLOTS_RUNNING

  SLOTS_RUNNING = True
  slot_to_roll = SLOTS[slot_series]
  files = os.listdir(slot_to_roll["files"])
  results = []
  
  for i in range(3):
    results.append(random.choice(files))

  matching_results = [s.replace(".png", "") for s in results]

  silly_matches = []

  #print("match results", matching_results)

  for match_title in slot_to_roll["matches"]:
    #print(f"Checking {match_title}...")
    matches = slot_to_roll["matches"][match_title]
    #print("matches to check", matches)
    match_count = 0
    for m in matches:
      if m in matching_results:
        match_count += 1
    if match_count >= 2:
      silly_matches.append(match_title)
  
  if generate_image:
    image1 = Image.open(slot_to_roll["files"] + results[0]).resize((150,150))
    image2 = Image.open(slot_to_roll["files"] + results[1]).resize((150,150))
    image3 = Image.open(slot_to_roll["files"] + results[2]).resize((150,150))
    
  matching_chars = []
  result_set = set(results)
  matching_results = [s.replace(".png", "") for s in result_set]
  jackpot = False

  if len(result_set) == 1:
    matching_chars.append(results[0].replace(".png", ""))
    jackpot = True

  if len(result_set) == 2:
    for r in result_set:
      if results.count(r) > 1:
        matching_chars.append(r.replace(".png", ""))

  logo = slot_series + "_logo.jpg"
  color = (0,0,0,100)

  if generate_image:
    get_concat_h_blank(image1,image2,image3,color,logo).save("./slot_results/"+str(filename)+".png")
  #print("silly matches", silly_matches)
  SLOTS_RUNNING = False
  return silly_matches, matching_chars, jackpot


def get_concat_h_blank(im1, im2, im3, color, logo):
  logo_location = "./slots/" + logo
  dst = Image.new('RGBA', (im1.width + im2.width + im3.width + 32, max(im1.height, im2.height, im3.height+16)), color)
  mask = Image.open(logo_location).convert('RGBA').resize((150,150))

  final_images = []
  originals = [im1, im2, im3]

  for i in range(1,3+1):
    img = Image.new('RGBA', (150,150), (0,0,0))
    img.paste(mask)
    img.paste(originals[i-1], (0,0), originals[i-1])
    final_images.append(img)

  dst.paste(final_images[0], (8, 8))
  dst.paste(final_images[1], (im1.width+16, 8))
  dst.paste(final_images[2], (im1.width+im2.width+24, 8))

  return dst


def register_player(user):
  
  keys = db.keys()
  old_id = str(user.mention)
  player_id = str(user.id)

  # handle old scores if they're in there
  if old_id in keys:
    old_points = db[old_id]
    player_data = {
      "name" : user.name,
      "mention" : user.mention,
      "score" : old_points,
      "spins" : 0
    }
    del db[old_id]
    db[player_id] = player_data

  # register brand new player
  if player_id not in keys:
    player_data = {
      "name" : user.name,
      "mention" : user.mention,
      "score" : 0,
      "spins" : 0
    }
    db[player_id] = player_data



  

client.run(os.getenv('TOKEN'))