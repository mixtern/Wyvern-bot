#pylint: disable=C0103, C0111, C0301, C0330, W0603
import discord
from base import config

client = {}
async def init(client_bot):
    global client
    client = client_bot

def is_root(member):
    return member.id == config.get("main.root_id")

def is_operator(member):
    if member.server is None:
        return is_root(member)
    elif member.server == get_server('Slightly Discordant'):
        return get_role(member.server, 'Super-Admin') in member.roles or \
                get_role(member.server, 'Admins') in member.roles
    return member.server.role_hierarchy[0] in member.roles

def get_server(servName):
    for serv in client.servers:
        if serv.name.lower() == servName.lower():
            return serv
    return None

def get_channel(server, chanName):
    for chan in server.channels:
        if chan.name.lower() == chanName.lower() or \
            chan.name.lower() == '#' + chanName.lower():
            return chan
    return server.get_channel(chanName[2:-1] if '#' in chanName else chanName)

def get_role(subject, roleName):
    for role in subject.roles:
        if role.name.lower() == roleName.lower():
            return role
    return None

def get_member(server, userName):
    userName = userName.lower()
    for member in server.members:
        if member.id == userName[2:-1] or member.name.lower() == userName or \
            member.nick is not None and member.nick.lower() == userName:
            return member
    for member in server.members:
        if member.name.lower().startswith(userName) or member.nick is not None \
            and member.nick.lower().startswith(userName):
            return member
    return None

async def send_message(channel, message):
    try:
        print('{} #{} {}: {}'.format(channel.server.name, channel.name,
                client.user, message[:2000]))
        await client.send_message(channel, str(message)[:2000])
    except discord.Forbidden:
        pass
    except discord.HTTPException:
        await client.send_message(channel,
                'Message failed. Result string exceeded limitation.')

async def send_message_with_image(channel, message, embed=None):
    try:
        print('{} #{} {}: {}'.format(channel.server.name, channel.name,
                client.user, message[:2000]))
        await client.send_message(channel, str(message)[:2000], embed)
    except discord.Forbidden:
        pass
    except discord.HTTPException:
        await client.send_message(channel,
                'Message failed. Result string exceeded limitation.')
