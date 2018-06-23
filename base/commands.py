#pylint: disable=C0103, C0111, C0301, C0330, W0603
import discord, asyncio, sys, random
from modules import found_modules
from base import config, util
import inspect

command_list = {}
external_handlers = []

class command(dict):
    def __init__(self, name, command, args, description, check = lambda m: True, is_private = False):
        dict.__init__(self)
        if not isinstance(name,str):
            print("invalid name")
            return
        if not inspect.iscoroutinefunction(command):
            print("invalid command")
            return
        if not (isinstance(args,str) or isinstance(description,str)):
            print("invalid description")
            return
        if is_private:
            private_commands.append(name)
        self.update({name:(command,args,description,check)})
        global command_list
        command_list = {**command_list, **self}
            

async def init(client_bot):
    global client
    client = client_bot
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return
        for hnd in external_handlers:
            if not inspect.iscoroutinefunction(hnd):
                continue
            await hnd(message)
        if '<@{}>'.format(client.user.id) in message.content:
            args = message.content[message.content.index(
                    '<@{}>'.format(client.user.id)) +
                len('<@{}>'.format(client.user.id)):].split(' ')
        elif '<@!{}>'.format(client.user.id) in message.content:
            args = message.content[message.content.index(
                    '<@!{}>'.format(client.user.id)) +
                len('<@!{}>'.format(client.user.id)):].split(' ')
        else:
            return
        args = [arg for arg in args if arg] #what
        if len(args) > 0 and args[0].lower() in meeps:
            random.choice([True, False])
            await util.send_message(message.channel, random.choice(meep_responses))
            return
        elif len(args) > 0 and args[0].lower() not in command_list and \
            (message.server is None or util.is_operator(message.author)):
            await util.send_message(message.channel, 
                'Unrecognized command `{}`.'.format(args[0]))
            return
        try:
            #print('{} #{} {}: {}'.format(message.server.name, 
            #message.channel.name, message.author.name, message.clean_content))
            await client.send_typing(message.channel)
            await command_list[args[0].lower()][0](message, args[1:])
        except discord.Forbidden:
            await util.send_message(message.channel,
                    'Message failed. Forbidden access.')

async def command_test(message, args):
    await util.send_message(message.channel, 'pong')

# are we 1-dimensional now, jd?
sassy_responses = ["ping",
                    "Meep. (Very funny.)",
                    "Meep, meep. (Wise guy over here.)",
                    "Meep, meep! (Hey, I can play both sides!)",
                    "Meep, meep, meep. (I'm not just some 1-dimensional bot.)",
                    "Ping. Meep? (Ping. What did you expect?)",
                    ]
async def command_test2(message, args):
    random.choice([True, False])
    await util.send_message(message.channel, random.choice(sassy_responses))

private_commands = ['logout', 'clean', 'update', 'config']
async def command_help(message, args):
    if len(args) == 0:
        result = '```\nUsage: @{} <command>\n'.format(client.user.name) + \
        '\nAvailable commands:\n'
        for k, v in command_list.items():
            if k not in private_commands:
                if v[3](message):
                    result += k + '\n'
        result += '```'
        #await util.send_message(message.channel, result[:-2])
        await util.send_message(message.channel, result)
    elif args[0].lower() in command_list:
        result = '`{1} {0[1]}`\n\n{0[2]}'.format(command_list[args[0].lower()], 
            args[0])
        await util.send_message(message.channel, result)
    else:
        result = 'Unrecognized command `{}`.'.format(args[0])
        await util.send_message(message.channel, result)

async def command_clean(message, args):
    if not util.is_root(message.author):
        await util.send_message(message.channel, 
                'Missing operator privileges.')
        return
    await util.send_message(message.channel, 'Acknowledged.')
    await client.purge_from(message.channel, limit=100,
        check=lambda m: m.author == client.user or client.user in m.mentions)

async def command_logout(message, args):
    if not util.is_root(message.author):
        await util.send_message(message.channel, 
                'Missing operator privileges.')
        return
    await util.send_message(message.channel, 'Acknowledged.')
    #for server in client.servers:
    #    if client.voice_client_in(server) is not None:
    #        await client.voice_client_in(server).disconnect()
    await client.logout()
    mods = [globals()[x] for x in found_modules]
    await client.close() #necessary?
    await asyncio.sleep(5) #necessary?
    for mod in mods:
        mod.client.loop.stop()
    client.loop.stop()
    sys.exit() #necessary?

command_list = {
    'ping' : (command_test, '', 'Request diagnostic reply.', lambda m: True),
    'pong' : (command_test2, '', '1-dimensional my butt.', lambda m: True),
    'help' : (command_help, '[command]',
                'Explain `command` if provided ' +
                'or list all available commands.',
                lambda m: True),
    'clean' : (command_clean, '',
                'Remove recent bot-related chatter for this bot.',
                lambda m: m.server is not None
                    and m.channel.permissions_for(m.server.me).manage_messages),
    'config' : (config.command_config, '[set/get/print/list]', 
        config.description,
                lambda m: len([x for x in m.author.roles if x.id == "320705908311064586"])
                 or util.is_root(m.author)),
    'logout' : (command_logout, '',
                '**Root Command**\nLogout this bot from all streams and connections.',
                lambda m: util.is_root(m.author))
}

meeps = [   'meep',
            'meep!',
            'meep?',
            'meeps',
            'meep-meep',
            'mah',
            'mah?',
            'mah!',
            'mahs',
]

meep_responses = [  "Meep?! (What did you say about my mother?!)",
                    "Mah! Meep mah! Mah! (Here's your prize! Please don't sue!)",
                    "Meep, mah mah. Meep meep. Mah mah meep. Meep, meep. (Yes.)",
                    "Mah, meep. Meep mah. Mah mah meep. Meep meep meep. Mah meep. (No.)",
                    "Mah! Meep! (Spoilers! Geez, I haven't gotten there yet!)",
                    "Meep meep mah! (T-that wasn't me, I swear!)",
                    "Meep mah mah! Meep mah! (I did not! I have no idea what you're talking about!)",
                    "Meep mah? (What's THAT supposed to mean?)",
                    "MEEP?! (You WHAT?!)",
                    "Mah meep. (What's a 'Crunky'?)",
                    "Mah meep?! Mah meep mah! (I told you, I'm not interested.)",
                    "Meep, meep! (Finally, someone talking sense!)", #teh_foxx0rz
                    "Meep meep! (I'm doing my best meep!)", #Gale
                    "Morp.", #JD
]