import youtube_dl
import asyncio, discord
from enum import Enum
from base import config,util
from base.commands import command,external_handlers

def cancel(self):
    self.after = None
    self.stop()

discord.voice_client.StreamPlayer.cancel = cancel

query = {}

async def command_play(message, args):
    await query.add(args[0])

cmd_play = command('play',command_play,'<url>',
'Queue the music found at url in the radio.\n'+
'See: https://rg3.github.io/youtube-dl/supportedsites.html')


async def command_skip(message, args):
    await util.send_message(message.channel, "Acknowledged.")
    if not query.is_playing:
        query.qlist.pop(0)
        config.set("music.query", query.qlist)
        return
    if (len(args)>0) and (args[0] == "all"):
        query.next(skip_all=True)
    else:
        if query.player is not None:
            query.player.cancel()
        query.next()

cmd_skip = command('skip', command_skip, '[all]',
'Skip current song in radio. Keyword all erases current playlist entirely.')

from urllib.parse import urlparse

def is_valid(url):
    try:
        result = urlparse(url)
        return result.scheme and result.netloc and result.path
    except:
        return False

async def on_message(message):
    if message.channel.id != config.get("music.channel"):
        return
    if len(message.embeds)>0:
        await check(message)
        for embed in message.embeds:
            await query.add(embed["url"])
        return
    urls = []
    for url in message.clean_content.split(" "):
        if is_valid(url):
            urls.append(url)
    print(message.clean_content)
    print(message.content)
    if len(urls) > 0:
        await check(message)
        for url in urls:
            await query.add(url)
        return
    if len(message.attachments)>0:
        await check(message)
        for attach in message.attachments:
            await query.add(attach["url"]) 
        return
        

async def check(message):
    await client.add_reaction(message,"✔")

external_handlers.append(on_message)


class States(Enum):
    STOPPED = 1
    CONNECTING = 2
    WAITING = 3
    PLAYING = 4


class Query:
    def __init__(self):
        if not isinstance(client,discord.Client):
            raise TypeError("provided object is not discord.Client")
        self.is_playing = False
        self.qlist = config.get("music.query")
        self.player = None
        self.voice = None
        self.state = States.STOPPED
        self.channel = client.get_channel(config.get("music.voice"))
        @client.event
        async def on_voice_state_update(before, after):
            await asyncio.sleep(1)
            await self.update()
    

    async def update(self):
        members = len(self.channel.voice_members)
        if (self.voice is not None) and self.voice.is_connected():
            members -= 1
        if len(self.qlist) == 0:
            await self.disconnect()
            return
        if (self.state == States.STOPPED) and members>0:
            await self.connect()
            await self.play()
        elif (members == 0) and self.state != States.STOPPED:
            await self.disconnect()

    async def connect(self):
        if (self.voice is not None) or (self.state != States.STOPPED):
            return
        self.voice = await client.join_voice_channel(self.channel)
        self.state = States.CONNECTING
        while not self.voice.is_connected():
            await asyncio.sleep(1)
        self.state = States.WAITING

    async def disconnect(self):
        if self.voice is None:
            return
        if self.player is not None:
            self.player.cancel()
            self.is_playing = False
        await self.voice.disconnect()
        self.voice = None
        self.state = States.STOPPED
        
    async def add(self, url, recursion = False):
        if not url:
            return
        ydl = youtube_dl.YoutubeDL()
        try:
            info = ydl.extract_info(url,download=False, process=False)
        except youtube_dl.utils.DownloadError:
            return
        if "entries" in info:
            for inf in info["entries"]:
                await self.add(inf['url'],recursion=True)
            return
        self.qlist.append(url)
        if not recursion:
            pass #check mark here
        if self.qlist.index(url) == 0 and len(self.qlist) == 1:
            await self.update()

    async def play(self):
        opts = {"buffersize":"16k","format":"bestaudio/worst"}
        self.player = await self.voice.create_ytdl_player(self.qlist[0],ytdl_options=opts)
        self.player.after = self.next
        self.player.start()
        self.is_playing = True
        self.state = States.PLAYING
        chan = client.get_channel(config.get("music.channel"))
        await util.send_message(chan,"Now playing: " + self.player.title + "\n <%s>" % self.player.url)
        config.set("music.query", self.qlist)

    def next(self, skip_all=False):
        if self.is_playing:
            self.qlist.pop(0)
        if self.player is not None:
            self.player.cancel()
            self.player = None
        if skip_all == True:
            self.qlist = []
        if len(self.qlist) == 0:
            asyncio.ensure_future(self.disconnect(), loop=client.loop)
            config.set("music.query", self.qlist)
            return
        asyncio.ensure_future(self.play(), loop=client.loop)



async def init(cli):
    global query,client
    client = cli
    @client.event
    async def on_reaction_add(reaction, user):
        print(reaction.emoji)
    query = Query()
    await query.update()
