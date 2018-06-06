#pylint: disable=C0103, C0111, C0301, C0330, W0603
import re
import sys, asyncio, datetime, logging, discord, traceback
import tweet, rss, config, commands, util, picarto
# from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.DEBUG)
client = discord.Client()

bot_id = config.main["bot_id"]

async def init():
    mods = [tweet, rss, commands, util, picarto, config]
    for mod in mods:
        await mod.init(client)

@client.event
async def on_ready():
    print('Logged in.')
    await init()
    for serv in client.servers:
        print('{} - {}'.format(serv.name, serv.role_hierarchy[0].name))
        for chan in serv.channels:
            print(' {} '.format
            (
                     '*' if chan.is_default
                #else '#' if (radios[serv] is not None and chan is radios[serv])
                #else '@' if chan.type == discord.ChannelType.voice
                else '+' if chan.permissions_for(serv.me).send_messages
                else '=' if chan.permissions_for(serv.me).read_message_history
                else '-' if chan.permissions_for(serv.me).read_messages
                else ' '
            ) + chan.name)
    await config.write('all')

@client.event
async def on_member_join(member):
    await client.send_message(member.server.default_channel, 
        'Welcome <@{}>! '.format(member.id) +
        'Make sure to check the rules in the ' +
        'pinned messages or <#{}>; '.format(config.main["welcome_id"]) + 
        'tell us if you accept them and we\'ll make you '
        'a member! This will grant you ' +
        'access to all chat and discussion channels ' +
        'on the server. <@&{}>'.format(config.main["staff_id"]))

@client.event
async def on_member_update(old_member, member):
    if len(old_member.roles) == 1 and len(member.roles) == 2 \
        and member.roles[1] == util.get_role(member.server, 'Member'):
        await client.send_message(
            client.get_channel(config.main["general_id"]),
            'Welcome to {}, <@{}>!'.format(member.server.name, member.id) )

async def on_error():
    client.logout()
    client.close() #necessary?
    await asyncio.sleep(60) #necessary?
    sys.exit() #necessary?

client.run(config.keys["discord"]["token"])
