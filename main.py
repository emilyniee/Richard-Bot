#################  SETTING UP VIRTUAL ENVIRONMENT
# py -3 -m venv venv
# venv\Scripts\activate
# python main.py

#################  IMPORTS
# pip install -U discord.py
# pip install Flask
# pip3 install --upgrade google-api-python-client
# pip install transformers
# pip3 install torch torchvision
# pip install --upgrade tensorflow
import discord
import os, os.path
from discord.ext import commands
import shutil
from Ping import _ping
from offender import Offender
from discord.ext.commands import Bot, has_permissions, CheckFailure, MissingPermissions
from googleapiclient import discovery

'''
from objprint import op
import torch
import numpy as np
from transformers import BertTokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# loading tokenzier and model for second toxicity classifier
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
model = torch.load('C:/toxicity_bot/epoch-1.pth', map_location=torch.device('cpu'))
'''

#keys
discord_token = "OTAzMjY5MzU3NjAwMjQ3ODI5.YXqhJA.VGd7sYzqGKvr_lfS6_Hc5Up97vw"
API_KEY = "AIzaSyDu2dfwRgU_S56o4pbI_dQCtT5drGclnM4"
COGS = 'log.py'

client = discord.Client()
bot = commands.Bot(command_prefix="!", case_insensitive=True, help_command=None)

clientAPI = discovery.build(
  "commentanalyzer",
  "v1alpha1",
  developerKey = API_KEY,
  discoveryServiceUrl = "https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
  static_discovery = False,
)

#################  FUNCTIONS
offenderDict={}
# shows number of strikes a user has
def showOffenderStrike(userID):
  if str(userID) in offenderDict:
    print(offenderDict[str(userID)].getStrike())
    user = offenderDict[str(userID)].getStrike()
    return user
  else:
    return False

# removes the strikes from a user
def resetOffender(userID):
  if str(userID) in offenderDict:
    offenderDict[str(userID)].strike = 0
    return True
  return False

# makes an object for a user that doesnt have a track record yet
def makeOffender(userID):
  #user = Offender(userID, 1)
  offenderDict[f'{userID}']=(Offender(userID, 1))
  return True

#updates the amount of stikes a user has
def updateOffender(userID):
  offenderDict
  if str(userID) in offenderDict:
    offenderDict[str(userID)].strike = int(offenderDict[str(userID)].strike)+1
    return True
  return False

# analyzes the toxicity of a message
def toxicity(message):
  try:
    analyze_request = {
      'comment': { 'text': message.content},
      'requestedAttributes': {'TOXICITY': {}}
	  }
    response = clientAPI.comments().analyze(body=analyze_request).execute()
    score = float(response['attributeScores']['TOXICITY']['summaryScore']['value'])
    return score
  except:
    print("Error with Perspective calculation")
    tempScore = 0
    return float(tempScore)

'''
# does the same thing as the previous funciton but with a different ml model
def toxicity2(message):
    # creating sentence and label lists
    sentence = str(message.content)

    # tokenizing
    input_ids = []

    encoded_sentence = tokenizer.encode(
                            sentence,                
                            add_special_tokens = True,
                    )
    input_ids.append(encoded_sentence)

    # padding
    input_ids = pad_sequences(input_ids, maxlen=256, 
                            dtype="long", truncating="post", padding="post")

    # creating attention masks
    attention_masks = []

    for seq in input_ids:
        seq_mask = [float(i>0) for i in seq]
        attention_masks.append(seq_mask) 

    # converting to tensor
    prediction_inputs = torch.tensor(input_ids)
    prediction_masks = torch.tensor(attention_masks)

    # putting model in evaluation mode
    model.eval()

    predictions = []
    
    #making predictions
    with torch.no_grad():
        outputs = model(prediction_inputs, token_type_ids=None, 
                        attention_mask=prediction_masks)

    # moving outputs to CPU and storing predictions
    predictions.append(outputs[0].detach().cpu().numpy())

    # turning predictions into 0 for nontoxic and 1 for toxic
    flat_predictions = [item for sublist in predictions for item in sublist]
    flat_predictions = np.argmax(flat_predictions, axis=1).flatten()

    #returning the classfication
    return flat_predictions[0]
'''

#################  CODING FOR THE BOT
# bot is loading in
@bot.event
async def on_ready():
  print('Logged in as')
  print(bot.user)
  print(bot.user.id)
  print('--------')

	#sets status so users know the help command
  await bot.change_presence(status=discord.Status.online, activity=discord.Game(name='!help'))
  

# if message starts with command !hello, sends hello to user
@bot.command( name = "hello")
async def hello(message):
  response = "Hello, " + str(message.author.display_name)
  await message.send(response)
  print("Said Hello to user: "+ str(message.author.display_name))

# to get the ping of the bot
@bot.command(name = "ping")
async def ping(ctx : commands.Context):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

# shows the amount of strikes of a specific individual
@bot.command(name = "showstrike", pass_context = True)
@commands.has_permissions(administrator = True)
async def showStrike(ctx, member:discord.Member):
  if(showOffenderStrike(member)) == False:
    embed = discord.Embed(title="User Clean", description="This user has no track record.")
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title="User Record", description="This user has " +str(showOffenderStrike(member))+ " strike(s)")
    await ctx.send(embed=embed)
# sends error if user is not admin
@showStrike.error
async def showStrikeError(message, error):
  if isinstance(error, commands.errors.CheckFailure):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)

# clears the track record of an offender
@bot.command(name = "clearstrike")
@commands.has_permissions(administrator = True)
async def clear(ctx, member:discord.Member):
  if(resetOffender(member)) == False:
    embed = discord.Embed(title="User Clean", description="This user has no track record.")
    await ctx.send(embed=embed)
  else:
    embed = discord.Embed(title="User Record Wiped", description="This user now has 0 strikes")
    await ctx.send(embed=embed)
# sends error if user is not admin
@clear.error
async def clearError(message, error):
  if isinstance(error, commands.errors.CheckFailure):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)

# mute a user (if the mute role in the server is called "Muted")
@bot.command(name = "mute")
@commands.has_permissions(administrator = True)
async def mute(ctx, member:discord.Member):
  role = discord.utils.get(ctx.guild.roles, id = 930857449123094548)
  await member.add_roles(role)

  embed=discord.Embed(title="User Muted")
  await ctx.send(embed=embed)
# sends error if user is not admin
@mute.error
async def muteError(message, error):
  if isinstance(error, commands.errors.CheckFailure):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)

# unmutes a user (takes the role restricting their permissions away)
@bot.command(name="unmute")
@commands.has_permissions(administrator = True)
async def unmute(ctx, member: discord.Member):
  mutedRole = discord.utils.get(ctx.guild.roles, id = 930857449123094548)
  await member.remove_roles(mutedRole)

  embed = discord.Embed(title="User Unmuted")
  await ctx.send(embed=embed)
# sends error if user is not admin
@unmute.error
async def unmuteError(message, error):
  if isinstance(error, commands.errors.CheckFailure):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)

# allows administrators to add words to the blacklist (automatically deleted words)
@bot.command(name = 'addbl', pass_context=True)
@commands.has_permissions(administrator = True)
async def _addbl(ctx, *arg):
  message_respond=""

  f = open("blacklist.txt", "a")
  
  message_respond = " ".join(arg)
  message_respond = message_respond.lower()

  if (message_respond[0]!='!'):
    already_blacklisted = False
    with open("blacklist.txt", 'r') as file:
      blacklist = [line.strip() for line in file]
    for i in range(len(blacklist)):
      if (str(blacklist[i]) == str(message_respond)):
        await ctx.send("Word is already in the blacklist")
        already_blacklisted = True
    if already_blacklisted == False:
      f.write(message_respond+"\n")
      f.flush()
      await ctx.send("Word added to the blacklist")
  f.close()
# sends error if user is not admin
@_addbl.error
async def addblError(message, error):
  if isinstance(error, commands.errors.CheckFailure):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)

# administrators can remove words from the blacklist
@bot.command(name = 'removebl', pass_context = True)
@commands.has_permissions(administrator = True)
async def _removebl(ctx, *arg):
  message_respond=""
  message_respond = " ".join(arg)
  message_respond = message_respond.lower()

  in_blacklist = False
  
  with open("blacklist.txt", 'r') as file:
    blacklist = [line.strip() for line in file]

  for i in range(len(blacklist)):
    if (str(blacklist[i]) == str(message_respond)):
      in_blacklist = True
      with open('blacklist.txt', 'r') as input:
        with open('tempbl.txt', 'w') as output:
          for line in input:
            if line.strip('\n') !=message_respond:
              output.write(line)
        shutil.copyfile('tempbl.txt', 'blacklist.txt')
        await ctx.send("Word removed from blacklist")
  
  if in_blacklist == False:
    await ctx.send("Word was never in the blacklist")
# sends error if user is not admin
@_removebl.error
async def removeblError(message, error):
  if isinstance(error, commands.errors.CheckFailure):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)  

# clears whole blacklist
@bot.command(name = "clearbl")
@commands.has_permissions(administrator = True)
async def clearbl(ctx):
  open('blacklist.txt','w').close()
  await ctx.send("blacklist has been cleared")
# sends error if user is not admin
@clearbl.error
async def clearblError(message, error):
  if isinstance(error, commands.errors.CheckFailure):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)  

# sends the current blacklisted words through direct messaging when command is used
@bot.command(name = "blacklist", pass_context = True)
async def DM(message):
  f = open("blacklist.txt", 'r')
  file_contents = f.read()
  
  if os.path.getsize('blacklist.txt') == 0:
    embed = discord.Embed(title = "Blacklist", description = 'There are no blacklisted words!')
    await message.channel.send(embed = embed)
  else:
    embed = discord.Embed(title = 'Blacklist', description = f'||{file_contents}||')
    await message.channel.send(embed = embed)
  f.close()

# sends list of users with strikes in dms to administrators who request it
@bot.command(name = "strikelist", pass_context = True)
@commands.has_permissions(administrator = True)
async def strikeList(message):

  embed = discord.Embed(title = "Strike List", description = 'The list of users and their strikes')
  
  for key in offenderDict:
    print(key)
    embed.add_field(name = key, value = showOffenderStrike(str(key)))
  
  dm = await message.author.create_dm()
  await dm.send(embed = embed)
  await message.channel.send("The list of offenders has been sent to direct messages")

# sends error if user is not admin
@strikeList.error
async def strikelistError(message, error):
  if isinstance(error, MissingPermissions):
    embed = discord.Embed(title="Permission Denied", description="You do not have the perms to use this command")
    await message.send(embed=embed)

  elif offenderDict == {}:
    await message.channel.send("No one in this server has a strike yet!")
   
  elif isinstance(error, commands.errors.CommandInvokeError):
    embed = discord.Embed(title = "Error:",description = 'I am unable to send you direct messages. :( You have direct messaging turned off for those you do not have added.')
    await message.channel.send(embed = embed)

# diplays list of available commands and their purpose when command !help is used
@bot.command()
async def help(message):
  embed = discord.Embed(title = 'User Guide', url = 'https://www.canva.com/design/DAE1jeoVHuY/view', colour=discord.Colour.green())
  embed.set_author(name="Help: list of available commands")
  embed.add_field(name='!help',value='Shows this message')
  embed.add_field(name='!hello',value='I say hello to you')
  embed.add_field(name='!ping',value='Shows the ping of the bot')
  embed.add_field(name='!blacklist', value='List of blacklisted words will be displayed')
  embed.add_field(name='!addbl ___', value='Administrators can add words to the blacklist')
  embed.add_field(name='!removebl ___', value='Administrators can remove contents from the blacklist')
  embed.add_field(name='!clearbl', value='Administrators can remove all contents from the blacklist')
  embed.add_field(name='!mute @___', value='Administrators can @ a user to mute them')
  embed.add_field(name='!unmute @___', value='Administrators can @ a user to unmute them')
  embed.add_field(name="!strikelist", value="Administrators will be sent a list of offenders through DMs")
  embed.add_field(name="!showstrike @___", value="Administrators can @ a user to see the number of offences they have")	 
  embed.add_field(name="!clearstrike @___", value="Administrators can @ a user to clear their strike history")	
  await message.send(embed=embed)

# reads over all messages to check for toxicity and if they contain words from the blacklist
@bot.event
async def on_message(message):
  await bot.process_commands(message)
  # when we check for specific words, we wont need to care about capitilization
  msg_content = message.content.lower()
  
  if "!" not in msg_content:
    # if message is from the bot, prevents bot from reacting to its own messages
    if message.author ==  bot.user:
      return

    print (str(message.author) +": " + str(message.content) + ' - ' + str(toxicity(message)))
    if toxicity(message) > 0.9:
      await message.delete()
    else:
      with open("blacklist.txt", 'r') as file:
        blacklist = [line.strip() for line in file]
      # deletes the message if there is a blacklisted word in it
      for i in range(len(blacklist)):
        if (str(blacklist[i]) in str(msg_content)):
          print(blacklist[i]) 
          print(msg_content)
          await message.delete()

# reports if a message was edited   
@bot.event
async def on_message_edit(before, after):
  await bot.process_commands(after)
  if (after.author.id == bot.user.id):
    return
  if before.content != after.content:
    channel = bot.get_channel(933038228657823824)

    embed = discord.Embed(title = "Edited Message", colour=discord.Colour.green())
    embed.add_field(name = f" {before.author}:", value = f"original: {before.content} \nedited: {after.content}")
    
    await channel.send(embed = embed)

    
    if toxicity(after)>0.9:
      await after.delete()
    
    with open("blacklist.txt", 'r') as file:
      blacklist = [line.strip() for line in file]
      # deletes the message if there is a blacklisted word in it
      for i in range(len(blacklist)):
        if (str(blacklist[i]) in str(after.content)):
          await after.delete()

# reports if a message was deleted
@bot.event
async def on_message_delete(message):
  message_content = message.content.lower()
  secret = False
  toxic = False
  if not message.author.bot:
    channel = bot.get_channel(933038228657823824)
    with open('blacklist.txt', 'r') as file:
      blacklist = [line.strip() for line in file]
    for i in range(len(blacklist)):
      if (str(blacklist[i]) in str(message_content)):
        secret = True
    if toxicity(message)>0.9:
      toxic = True
    if secret is True:	
      if updateOffender(message.author) == False:
        makeOffender(message.author)

      embed = discord.Embed(title = "Offender warning", colour=discord.Colour.red())
      embed.add_field(name = str(message.author), value = "Strike: " + str(offenderDict[str(message.author)].getStrike()) + "\nReason: Used blacklisted word")
      await message.channel.send(embed = embed)
        
      embed = discord.Embed(title = "Deleted Message by Richard: Blacklist", colour=discord.Colour.red())	
      embed.add_field(name = 'By ' + str(message.author) + ' in ' + str(message.channel)+':', value = str(f'||{message.content}||'))
      await channel.send(embed = embed)
      
    elif toxic is True:
      if updateOffender(message.author) == False:
        makeOffender(message.author)			
      embed = discord.Embed(title = "Offender warning", colour=discord.Colour.red())
      embed.add_field(name = str(message.author), value = "Strike: " + str(offenderDict[str(message.author)].getStrike()) + "\nReason: Toxic message")
      await message.channel.send(embed = embed)			
      embed = discord.Embed (title = "Deleted Message by Richard: Toxic", colour = discord.Colour.red())
      embed.add_field(name = 'By ' + str(message.author) + ' in ' + str(message.channel)+':', value = str(f'||{message.content}||'))
      await channel.send(embed = embed)			

    else:
      embed = discord.Embed (title = "Deleted Message", colour = discord.Colour.green())
      embed.add_field(name = 'By ' + str(message.author) + ' in ' + str(message.channel)+':', value = str(message.content))
      await channel.send(embed = embed)

# run Ping code: makes web server which gets pings every 5 mins
_ping()

# bot will run
bot.run(discord_token)