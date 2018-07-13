import json, discord, asyncio

description = 'set [path.separated.by.dots] [value] - assigns value to variable in config\n' \
              'get [path.separated.by.dots] - value of variable from config\n' \
              'print [config] - prints selected config in JSON format \n' \
              'list - prints all available config_list\n'

client = discord.Client()
async def init(cli):
    global client
    client = cli

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

config_list = { 'rss'       : "config/rss.json",
                'main'      : "config/main.json",
                'tweet'     : "config/tweet.json",
                'keys'      : "config/keys.json",
                'picarto'   : 'config/picarto.json',
                'music'     : 'config/music.json'
                }
configs = {}
for config in config_list:
    path = config_list[config]
    test = json.load(open(path, 'r'))
    configs[config] = test

def write(s=''):
    if s in config_list:
        f = open(config_list[s], 'w')
        f.write(json.dumps(configs[s], sort_keys="true", indent=4))
    else:
        for config in config_list:
            f = open(config_list[config], 'w')
            f.write(json.dumps(configs[config], sort_keys="true", indent=4))

def get(path):
    path = path.split('.')
    if path[0] in config_list:
        var = configs
        for x in path:
            var = var[x]
        return var

def set(path, value):
    path = path.split('.')
    if path[0] in config_list and path[0] != 'keys':
        path_str=''
        for x in path:
            if is_number(x):
                path_str += '[%s]' % x
            else:
                path_str += '["%s"]' % x
        command = 'configs' + path_str + ' = value'
        exec(command)
        write(path[0])

async def command_config(message, args):
    channel = message.channel

    async def conf_set(path, value):
        unsplit = path
        path = path.split('.')
        if path[0] in config_list and path[0] != 'keys':
            path_str = ''.join(['["%s"]' % x for x in path])
            command = 'configs' + path_str + ' = eval(value)'
            exec(command)
            write(path[0])
            await client.send_message(channel, 'value %s was assigned to %s' % (value, unsplit))

    async def conf_get(path):
        unsplit = path
        path = path.split('.')
        if path[0] in config_list and path[0] != 'keys':
            var = configs
            for x in path:
                var = var[x]
            await client.send_message(channel, '%s = %s' % (unsplit, var))

    async def conf_print(config):
        if config in config_list and config != 'keys':
            await client.send_message(channel, 
                config_list[config] + ':\n```' + 
                json.dumps(configs[config], sort_keys="true", indent=4) + '```')

    async def conf_list():
        await client.send_message(channel, ', '.join((x for x in config_list if x != 'keys')))

    options = {'set': (conf_set, 3), 'get': (conf_get, 2), 'print': (conf_print, 2), 'list': (conf_list, 1)}
    if args[0] in options:
        if options[args[0]][1] == len(args):
            await options[args[0]][0](*args[1:])
