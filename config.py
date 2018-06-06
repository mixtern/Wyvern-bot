import json, discord, asyncio

description = 'set [path.separated.by.dots] [value] - assigns value to variable in config\n' \
              'get [path.separated.by.dots] - value of variable from config\n' \
              'print [config] - prints selected config in JSON format \n' \
              'list - prints all available configs\n'

client = discord.Client()
async def init(cli):
    global client
    client = cli

configs = {'rss': "config/rss.json",
           'main': "config/main.json",
           'tweet': "config/tweet.json",
           'keys': "config/keys.json",
           'picarto': 'config/picarto.json'}

for config in configs:
    path = configs[config]
    test = json.load(open(path, 'r'))
    globals()[config] = test

async def write(s=''):
    if s in configs:
        f = open(configs[s], 'w')
        f.write(json.dumps(globals()[s], sort_keys="true", indent=4))
    else:
        for config in configs:
            f = open(configs[config], 'w')
            f.write(json.dumps(globals()[config], sort_keys="true", indent=4))


async def command_config(message, args):
    channel = message.channel

    async def conf_set(path, value):
        unsplit = path
        path = path.split('.')
        if path[0] in configs and path[0] != 'keys':
            path_str = ''.join(['["%s"]' % x for x in path])
            command = 'globals()' + path_str + ' = eval(value)'
            exec(command)
            await write(path[0])
            await client.send_message(channel, 'value %s was assigned to %s' % (value, unsplit))

    async def conf_get(path):
        unsplit = path
        path = path.split('.')
        if path[0] in configs and path[0] != 'keys':
            var = globals()
            for x in path:
                var = var[x]
            await client.send_message(channel, '%s = %s' % (unsplit, var))

    async def conf_print(config):
        if config in configs and config != 'keys':
            await client.send_message(channel, configs[config] + ':\n```'+json.dumps(globals()[config], sort_keys="true", indent=4)+'```')

    async def conf_list():
        await client.send_message(channel, ', '.join((x for x in configs if x != 'keys')))

    options = {'set': (conf_set, 3), 'get': (conf_get, 2), 'print': (conf_print, 2), 'list': (conf_list, 1)}
    if args[0] in options:
        if options[args[0]][1] == len(args):
            await options[args[0]][0](*args[1:])
