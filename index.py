#pylint: disable=C0103, C0111, C0301, C0330, W0603
import re
import sys, asyncio, datetime, logging, discord, traceback
from base import config, commands, util
from modules import *
# from concurrent.futures import ProcessPoolExecutor

logging.basicConfig(level=logging.DEBUG)
client = discord.Client()

bot_id = config.get("main.bot_id")

async def init():
    for mod in [config,commands,util]:
        await mod.init(client)
    print("%d modules found:" % len(found_modules))
    print(", ".join(found_modules))
    for mod in found_modules:
        await globals()[mod].init(client)

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
    config.write('all')

@client.event
async def on_member_join(member):
    await client.send_message(member.server.default_channel, 
        'Welcome <@{}>! '.format(member.id) +
        'Make sure to check the rules in the ' +
        'pinned messages or <#{}>; '.format(config.get("main.welcome_id")) + 
        'tell us if you accept them and we\'ll make you '
        'a member! This will grant you ' +
        'access to all chat and discussion channels ' +
        'on the server. <@&{}>'.format(config.get("main.staff_id")))

@client.event
async def on_member_update(old_member, member):
    if len(old_member.roles) == 1 and len(member.roles) == 2 \
        and member.roles[1] == util.get_role(member.server, 'Member'):
        await client.send_message(
            client.get_channel(config.get("main.general_id")),
            'Welcome to {}, <@{}>!'.format(member.server.name, member.id) )

async def on_error():
    client.logout()
    client.close() #necessary?
    await asyncio.sleep(60) #necessary?
    sys.exit() #necessary?

client.run(config.get("keys.discord.token"))