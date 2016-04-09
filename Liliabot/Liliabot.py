import asyncio
import datetime as date
import time
import re
import discord as ds
import JukeBox as juke

#TODO:
#Fix process permissions to work on raspberry pi
ready = False
now = date.datetime.now()
client = ds.Client()
schedule = []
subscribers = []
#jukebox = juke.JukeBox(client)
timeRE = r'^([0-9]|0[0-9]|1?[0-9]|2[0-3]):[0-5]?[0-9]$'
dateRE = r'^(?:(?:31(\/|-|\.)(?:0?[13578]|1[02]))\1|(?:(?:29|30)(\/|-|\.)(?:0?[1,3-9]|1[0-2])\2))(?:(?:1[6-9]|[2-9]\d)?\d{2})$|^(?:29(\/|-|\.)0?2\3(?:(?:(?:1[6-9]|[2-9]\d)?(?:0[48]|[2468][048]|[13579][26])|(?:(?:16|[2468][048]|[3579][26])00))))$|^(?:0?[1-9]|1\d|2[0-8])(\/|-|\.)(?:(?:0?[1-9])|(?:1[0-2]))\4(?:(?:1[6-9]|[2-9]\d)?\d{2})$'
with open('Schedule') as f:
    content = f.readlines()
    content = [x.strip('\n') for x in content]
    for line in content:
        segment = line.split(' ')
        schedule.append((segment[0], segment[1], segment[2])) 

#opus.dll for windows, libopus.so for linux
#if not ds.opus.is_loaded():
    #ds.opus.load_opus('D:\Personal projects\Python\LiliaBot\LiliaBot\Liliabot\opus.dll')
print(ds.opus.is_loaded())



@client.event
async def on_ready():
    print('Logged in as')
    print(client.user.name)
    print(client.user.id)
    print(client.user.avatar)
    subscriberIds = []
    with open('Subscribers') as f:
        content = f.readlines()
        content = [x.strip('\n') for x in content]
        for line in content:
            subscribers.append(client.get_channel(line))              
    print('------')        
    while(True):               
        now = date.datetime.now()
        if(now.hour == 10):
            for channel in subscribers:  
                print(channel.name)
                await client.send_message(channel, "Ohaiyo everyone! Did you have a good night of sleep? I'll check any tasks for today now!")
                await CheckToday(channel, False) 
        print('Checking the hour.. nyaaaa..')
        await asyncio.sleep(3600)

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.lower().startswith('!test'):
        counter = 0
        tmp = await client.send_message(message.channel, 'Calculating messages...')
        async for log in client.logs_from(message.channel, limit=100):
            if log.author == message.author:
                counter += 1
        await client.edit_message(tmp, 'You have {} messages.'.format(counter))
    
    elif message.content.lower().startswith('!join '):
        if len(message.content[6:]) > 0:
            await JoinVoiceChannel(message.channel, message.content[6:])

    elif message.content.lower().startswith('!disconnect voice'):
        await DisconnectVoice(message.channel)

    elif message.content.lower().startswith('!addsong '):            
        await jukebox.AddSong(client, message, message.content[9:])

    elif message.content.lower().startswith('!play'):
        await jukebox.PlaySong(client, message.channel)

    elif message.content.lower().startswith('!skip'):
        await jukebox.SkipSong(client, message.channel)

    elif message.content.lower().startswith('!pause'):
        await jukebox.PauseSong(client, message.channel)

    elif message.content.lower().startswith('!resume'):
        await jukebox.ResumeSong(client, message.channel)
 
    elif message.content.lower().startswith('!stop'):
        await jukebox.StopPlayer(client, message.channel)

    elif message.content.startswith('!sleep'):
        await asyncio.sleep(5)
        await client.send_message(message.channel, 'Done sleeping')

    elif message.content.lower().startswith('!subscribe'):
        if message.channel in subscribers:
            subscribers.remove(message.channel)
            await client.send_message(message.channel, "Unsubscribed you for now... will you be back to play with me soon?")
        else:
            subscribers.append(message.channel)            
            await client.send_message(message.channel, "Subscribed you! Let's have a lot of fun, okay?")
        f = open('Subscribers', 'w')
        for channel in subscribers:
            f.write(channel.id)
        f.close()
    elif message.content.lower().startswith('!tableflip'):    
        await client.send_message(message.channel, '/tableflip')

    elif message.content.lower().startswith('!putthetableback'):
        await client.send_message(message.channel, '/unflip')

    elif message.content.lower().startswith('!yes'):          
        await client.send_message(message.channel, 'https://www.youtube.com/watch?v=P3ALwKeSEYs')

    elif message.content.lower().startswith("!don't be mean to lily") or message.content.lower().startswith("!don't be mean to lilychan") or message.content.lower().startswith("!dont' be mean to lilia"):
        await client.send_message(message.channel, "Please don't be mean to me! I'll be a good girl!")

    elif message.content.lower().startswith('!cute') or message.content.lower().startswith('!kawaii'):          
        await client.send_message(message.channel, ('♡＾▽＾♡'))

    elif message.content.lower().startswith('!marco'):          
        await client.send_message(message.channel, 'polo!')

    elif message.content.lower().startswith('!clearschedule'):
        schedule.clear()
        f = open('Schedule', 'w')
        f.close()
        await client.send_message(message.channel, "Cleared the schedule.. break time for me too now?")          

    elif message.content.lower().startswith('!setschedule'):
        line = message.content.split(" ")
        if(len(line) < 4):
            await client.send_message(message.channel, "No, no, not like that! Do it like this: !setschedule name_of_event DD/MM/YYYY HH:MM.")
            return
        if(re.match(dateRE, line[2]) != None):
            if(re.match(timeRE, line[3]) != None):
                schedule.append((line[1], line[2], line[3]))
                f = open('Schedule', 'a')
                f.write('%s %s %s\n' %(line[1], line[2], line[3]))
                f.close()
                await client.send_message(message.channel, "Set '%s' at %s, %sST!" % (line[1], line[2], line[3]))
            else:            
                await client.send_message(message.channel, "Baka! You didnt fill in a valid time! Try it like so: HH:MM")
        else:
            await client.send_message(message.channel, "You didn't do it right! You should fill in a valid date either DD/MM/YYYY, DD-MM-YYYY or DD.MM.YYYY. Now do it correctly!")
    elif message.content.lower().startswith('!schedule'):
        if(schedule == []):
            if(message.author.name == "Oblition"):
                 await client.send_message(message.channel, "Nothing set yet, today is free! Do you want to go out with me, Onii-chan?")
            else:
                await client.send_message(message.channel, "Nothing set yet, today is free!")
        else:
            line = message.content.split()
            response = ""
            if(len(line) >= 2):
                triggered = False                
                for (name, day, time) in schedule:
                    if(line[1].lower() in name.lower()):
                        if(not(triggered)):
                            triggered = True                            
                            await client.send_message(message.channel, "I found events planned for things like '%s'!" % (line[1]))						
                        response += "\n'%s' at %s, %sST!" %(name, day, time)
                if(not(triggered)):                    
                    await client.send_message(message.channel, "Couldn't find anything with that name. Aren't you lucky and free?")
                else:
                    await client.send_message(message.channel, response)
            elif(len(line) == 1):    
                await client.send_message(message.channel, "All the events that have been planned, coming right up!")
                for (name, day, time) in schedule:
                    response += "\n'%s' at %s, %sST!" % (name, day, time)
                await client.send_message(message.channel, response)
    elif message.content.lower().startswith('!today'):
        await CheckToday(message.channel, message.author.name == "Oblition")
              
async def CheckToday(channel, isObli):    
    if(schedule == []):            
        if(isObli):            
            await client.send_message(channel, "Nothing set for today, Obli-chan! Spend the day with me!")
        else:
            await client.send_message(channel, "Nothing set for today! Maybe you can spend the day with me instead?")
    else:
        triggered = False
        for(name, day, time) in schedule:
            if((date.datetime.today() - date.datetime.strptime(day, "%d/%m/%Y")).days == 0):
                if(not(triggered)):
                    triggered = True                         
                    await client.send_message(channel, "There is stuff to do today! It seems the following is set:")
                await client.send_message(channel, "'%s' at %sST!" %(name, time))
        if(not(triggered)):                
            if(isObli):            
                await client.send_message(channel, "Nothing set for today, Obli-chan! Spend the day with me!")
            else:
                await client.send_message(channel, "Nothing set for today! Maybe you can spend the day with me instead?")

async def JoinVoiceChannel(source, requestedChannel):
    channel = None
    print("Attempting voice channel joining!")
    for c in source.server.channels:
        if c.name == requestedChannel and c.type == ds.ChannelType.voice:
            channel = c
            break
    if channel == None:
        await client.send_message(source, "Couldn't find a voice channel with that name on this server... are you sure you did it right? Text channels don't count!")
    else:
        if client.voice == None or not(client.voice.is_connected()):            
            await client.send_message(source, "I'll try to join that voice channel, okai? Give me a moment!")
            await client.join_voice_channel(channel)
        else:
            await client.send_message(source, "I'm already connected to voice! If you want me to join that one, you should have me leave first.")
        
async def DisconnectVoice(source):
    print("Attempting disconnecting voice channel!")
    if client.voice != None and not(client.voice.is_connected()):
        await client.send_message(source, "You silly, how can I leave a voice channel I'm not even connected to?")
    else:
        await client.send_message(source, "Disconnecting from voice now.. come listen to me soon, please?")
        await client.voice.disconnect()

client.run('LiliaBloomheart@gmail.com', 'Lifeblossom345')
