from discord.ext import commands

from functions import *
from settings import token

description = '''What are you doing? Why don't you get yourself a teddy bear?'''

bot = commands.Bot(command_prefix=['!', '+'], description=description,
                   command_not_found='Command not recognized. Try the ``!help`` command.')

extensions = [
    'cogs.matchmaking',
    'cogs.moderation',
    'cogs.groups'
]


@bot.event
async def on_ready():
    botInfo = await bot.application_info()
    oauthlink = discord.utils.oauth_url(botInfo.id)

    print('---------')
    print('Username: {}'.format(bot.user.name))
    print('ID: {}'.format(bot.user.id))
    print('Server count: {}'.format(str(len(bot.servers))))
    print('Member count: {}'.format(str(len(set(bot.get_all_members())))))
    print('OAuth URL: {}'.format(oauthlink))
    print('Cogs: {}'.format(bot.cogs))
    print('---------')


@bot.event
async def on_member_join(member):
    if member.server.id == "228244312041848833":
        message = "{} Welcome to the PSO2 Matchmaking Server! Please type ``!reg \"YourPlayerID\"``(don't forget the quotes!) to receive full access to the server.".format(member.mention)
        await bot.send_message(discord.Object("228245872616407040"), message)

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}\n{}: {}'.format(extension, type(e).__name__, e))

    bot.loop.create_task(group_board(bot))
    bot.loop.create_task(activity_monitor(bot))
    bot.run(token)
