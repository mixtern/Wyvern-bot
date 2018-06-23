import asyncio, discord, feedparser, urllib.parse
from base import config,util
from base.commands import command
# from concurrent.futures import ProcessPoolExecutor

force = 0
client = {}

async def command_update(message, args):
    global force
    force = 1

cmd_update = command('update',command_update,'',
'Forcing page update test',check = lambda m: util.is_root(m.author))


async def init(cli):
    global client
    client = cli
    asyncio.ensure_future(do(), loop=client.loop)

async def do():
    global force, client
    # global counter
    
    while True:
        for y in range(len(config.get("rss.feeds"))):
            # get current link
            x = config.get("rss.feeds")[y]
            #print(x)
            d = feedparser.parse(x["url"])
            try:
                d.entries[0]
            except IndexError:
                print("Index Error with entries reached.\n")
                return
            try:
                d.entries[0].links[0]
            except IndexError:
                print("Index Error with links reached.\n")
                return
            post = d.entries[0].links[0].href
            summary = d.entries[0].summary
            image_link = urllib.parse.quote(summary[summary.find("src")+5:summary.find("\"", summary.find("src")+5)], [47, 58])
            # check and post the update
            if (x["last"] != post) or force:
                image = discord.Embed().set_image(url=image_link)
                message = x['message'] + "\n" + post
                dl_channel = client.get_channel(config.get("main.alert_id"))
                await client.send_message(dl_channel, message, embed=image)
            # update config file
            config.set("rss.feeds.%s.last" % y, post)
            force = 0
        # print("%d"%counter)
        # counter += 1
        for _ in range(config.get("rss.delay")):
            await asyncio.sleep(1, loop=client.loop)
            if force:
                break
    