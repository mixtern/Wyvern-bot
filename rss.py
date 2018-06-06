import asyncio, discord, feedparser, config, urllib.parse, util
# from concurrent.futures import ProcessPoolExecutor

force = 0
client = {}
# counter = 0

async def init(cli):
    global client
    client = cli
    # executor = ProcessPoolExecutor(1)
    # rss_do = asyncio.ensure_future(loop.run_in_executor(executor, loop.create_task(do())))
    asyncio.ensure_future(do(), loop=client.loop)

async def do():
    global force, client
    # global counter
    
    while True:
        for y in range(len(config.rss["feeds"])):
            # get current link
            x = config.rss["feeds"][y]
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
                dl_channel = client.get_channel(config.main["alert_id"])
                await client.send_message(dl_channel, message, embed=image)
            # update config file
            config.rss["feeds"][y]["last"] = post
            force = 0
        await config.write('rss')
        # print("%d"%counter)
        # counter += 1
        for _ in range(config.rss['delay']):
            await asyncio.sleep(1, loop=client.loop)
            if force:
                break
    
async def command_update(message, args):
    global force
    force = 1
