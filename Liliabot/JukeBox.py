import asyncio
import discord as ds

#TODO:
#Finetuning transitions

class Track:
    def __init__(self, message, song):
        self.sender = message.author
        self.source = message.channel
        self.song = song

class JukeBox():
    def __init__(self, client):
        self.player = None
        self.songs = asyncio.Queue()
        self.nextSong = asyncio.Event()
        self.currentSong = None
        self.client = client
        self.active = False
        self.skipping = False
         
    def is_playing(self):
        return self.player is not None and self.player.is_playing()

    def is_paused(self):
        return self.player is not None and self.player.is_done() and self.player.is_playing()

    def _kill_player(self):
        if self.player != None:
            self.player.stop()
            self.player = None
    
    def _set_next_song(self):
        self.client.loop.call_soon_threadsafe(self.nextSong.set)

    async def AddSong(self, client, message, song):
        await self.songs.put(Track(message, song))
        await client.send_message(message.channel, "Accepted your submission! Please look forward to it!")

    async def PlaySong(self, client, source):  
        if client.voice == None or not(client.voice.is_connected()):
            await client.send_message(source, "If I play this song now, you won't even hear it! Don't you want my cute self in a voice channel?")
            return
        elif self.is_playing():
            await client.send_message(source, "The jukebox is already active! Resume, add a song or check your volume settings.")
            return
        self.active = True
        while self.active:
            if client.voice == None or not(client.voice.is_connected()):
                return
            await self.PlaySongHandler(client)

    async def PlaySongHandler(self, client):    
        self.nextSong.clear()
        self.currentSong = await self.songs.get()
        self.player = await client.voice.create_ytdl_player(self.currentSong.song, after= self._set_next_song)
        self.player.start()         
        while self.active and (self.is_playing() or self.is_paused()):
            await asyncio.sleep(1.5)
        print("Done waiting!")

    async def PauseSong(self, client, source):
        if self.is_paused() or self.player == None:
            await client.send_message(source, "How am I supposed to pause something that isn't there, you goof?")
        else:
            self.player.pause()
            await client.send_message(source, "A brief pause, for now..")

    async def ResumeSong(self, client, source):
        if not(self.is_paused) or self.player == None:
            await client.send_message(source, "But there is nothing to resume!")
        else:
            self.player.resume()
            await client.send_message(source, "Resuming! You can't stop the music!")


    async def StopPlayer(self, client, source):
        if not(self.is_playing()) and not(self.is_paused()):
            await client.send_message(source, "I can't possibly stop it! I can only hope to contain it!")
        else:
            self.active = False
            self._kill_player()
            await client.send_message(source, "Putting the hammer down on the jukebox!")

    async def SkipSong(self, client, source):   
        if not(self.is_playing()) and not(self.is_paused()): 
            await client.send_message(source,"But there is nothing to skip!")
        else:
            self._kill_player()
            await client.send_message(source, "Skipping the song.. give me a moment!")
   