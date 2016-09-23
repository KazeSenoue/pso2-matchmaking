import asyncio
import datetime
import json

import discord
import pytz


async def group_board(bot):
    while not bot.is_closed:
        await bot.wait_until_ready()

        users = ReadFile('cogs/json/users.json')
        file = ReadFile('cogs/json/matchmaking.json')

        string = ":arrow_right: **GROUP BOARD**\n``ID.`` Quest name (1/12) - Group Owner\n\n"
        groups = []
        for group in file['groups']:
            groups.append("``{0:02d}.`` {1} ({2}/{3}) - {4}".format(group['id'], group['quest'], len(group['members']), group['maxmembers'], users[group['owner']]))

        groups = sorted(groups)
        channel = bot.get_channel("228245811048349696")
        message = await bot.get_message(channel, "228318470486360064")
        await bot.edit_message(message, string + "\n".join(groups))

        await asyncio.sleep(10)  # task runs every 10 seconds

async def activity_monitor(bot):
    while not bot.is_closed:
        await bot.wait_until_ready()

        try:
            for channel in bot.get_server("228244312041848833").channels:
                if channel.name.startswith("group-"):
                    id = int(channel.name.split('-')[1])
                    if datetime.datetime.now(pytz.utc) >= channel.created_at.replace(tzinfo=pytz.utc) + datetime.timedelta(hours=24):
                        file = ReadFile('cogs/json/matchmaking.json')

                        server = bot.get_server("228244312041848833")
                        for user in file['groups'][id]['members']:
                            await bot.remove_roles(server.get_member_named(user),
                                                        discord.utils.get(server.roles,
                                                                          name="Group {}".format(id)))

                        await bot.delete_channel(
                            discord.utils.get(server.channels, name="group-{}".format(id)))
                        await bot.delete_role(server,
                                                   discord.utils.get(server.roles, name="Group {}".format(id)))

                        file['groups'].pop(id)

                        with open('cogs/json/matchmaking.json', 'w+') as outfile:
                            json.dump(file, outfile, indent=4, sort_keys=True)
        except RuntimeError as e:
            pass

        await asyncio.sleep(5)

def ReadFile(file):
    with open(file, 'r') as file:
        file = json.load(file)
        return file

def WriteFile(file, data):
    with open(file, 'w+') as outfile:
        json.dump(data, outfile, indent=4, sort_keys=True)

def SearchGroup(groupid):
    file = ReadFile('cogs/json/matchmaking.json')
    index = 0
    for group in file['groups']:
        if groupid == group['id']:
            return index
        index += 1

def SearchMember(name):
    users = ReadFile('cogs/json/users.json')
    return list(users.keys())[list(users.values()).index(name)]