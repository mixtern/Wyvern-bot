import asyncio, discord, aiohttp, json, config, util

client = {}

async def init(cli):
    global client
    client = cli
    loop = client.loop
    asyncio.ensure_future(check(), loop=loop)

async def is_online(name):
    async with aiohttp.ClientSession() as session:
        response = await \
            session.get('https://api.picarto.tv/v1/channel/name/' + name)
        text = await response.text()
        try:
            result = json.loads(text)
        except json.decoder.JSONDecodeError:
            print("Picarto: no data in text. Returning False.\n")
            result = {'online': False}

        await session.close()
        # print('online' if result['online'] else 'offline')
        return result['online']

async def check():
    global client
    loop = client.loop
    streamers = config.picarto["streamers"]
    dl_channel = client.get_channel(config.main["alert_id"])
    online = []

    while True:
        for streamer in streamers:
            if await is_online(streamers[streamer]):
                if streamer in online:
                    continue
                else:
                    link = "http://picarto.tv/" + streamers[streamer]
                    message = config.picarto["announcement"] % streamer \
                        + '\n' + link
                    asyncio.ensure_future(client.send_message(dl_channel,
                        message), loop)
                    #await client.send_message(chan, 
                    #    config.picarto["announcement"] % streamer + '\n' + link)
                    online.append(streamer)
            elif streamer in online:
                online.remove(streamer)
        await asyncio.sleep(config.picarto["delay"], loop=loop)
