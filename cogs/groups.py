import threading

import discord
from discord.ext import commands

from functions import ReadFile, WriteFile, SearchGroup, SearchMember


class Group:
    """Group commands"""

    def __init__(self, bot):
        self.bot = bot
        self.lock = threading.RLock()

    @commands.group(pass_context=True)
    async def group(self, ctx):
        """Group commands"""

        if ctx.invoked_subcommand is None:
            await self.bot.say("{} You didn't input a subcommand. Try ``!help group``".format(ctx.message.author.mention))

    @group.command(pass_context=True)
    async def finish(self, ctx):
        with self.lock:
            if ctx.message.channel.name.startswith('group'):
                id = ctx.message.channel.name.split('-')[1]

                index = SearchGroup(int(id))
                file = ReadFile('cogs/json/matchmaking.json')

                if ctx.message.author.id == file['groups'][index]['owner']:
                    server = self.bot.get_server("228244312041848833")
                    for user in file['groups'][index]['members']:
                        await self.bot.remove_roles(server.get_member(user),
                                                    discord.utils.get(ctx.message.server.roles,
                                                                      name="Group {}".format(id)))

                    await self.bot.delete_channel(
                        discord.utils.get(ctx.message.server.channels, name="group-{}".format(id)))
                    await self.bot.delete_role(server,
                                               discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)))

                    file['groups'].pop(index)

                    WriteFile('cogs/json/matchmaking.json', file)
                else:
                    await self.bot.say(
                        "{} Only the group owner can finish the quest.".format(ctx.message.author.mention))
            else:
                await self.bot.say(
                    "{} Group commands must be used in a group channel.".format(ctx.message.author.mention))

    @group.command(pass_context=True)
    async def leave(self, ctx):
        """Leaves the selected group."""

        with self.lock:
            if ctx.message.channel.name.startswith('group'):
                groupID = ctx.message.channel.name.split('-')[1]
                file = ReadFile('cogs/json/matchmaking.json')
                index = SearchGroup(int(groupID))

                #print(file['groups'][groupID]['owner'])
                #print(file['groups'][index]['owner'])

                if ctx.message.author.id in file['groups'][index]['members']:
                    await self.bot.remove_roles(ctx.message.author,
                                                discord.utils.get(ctx.message.server.roles, name="Group {}".format(groupID)))

                    file['groups'][index]['members'].remove(ctx.message.author.id)

                    WriteFile('cogs/json/matchmaking.json', file)

                    await self.bot.say(
                        "{} You have been removed from the ``{}`` group.".format(ctx.message.author.mention,
                                                                                 file['groups'][index]['quest']))
                else:
                    await self.bot.say("{} You are not in that group.".format(ctx.message.author.mention))
            else:
                await self.bot.say(
                    "{} Group commands must be used in a group channel.".format(ctx.message.author.mention))

    @group.command(pass_context=True)
    async def remove(self, ctx, *, member: str):
        """Removes a selected member from a group. GROUP OWNER ONLY"""

        with self.lock:
            if ctx.message.channel.name.startswith('group'):
                groupID = ctx.message.channel.name.split('-')[1]
                member = SearchMember(member)

                file = ReadFile('cogs/json/matchmaking.json')
                index = SearchGroup(int(groupID))

                if ctx.message.author.id == file['groups'][index]['owner']:
                    try:
                        await self.bot.remove_roles(ctx.message.server.get_member(member),
                                                    discord.utils.get(ctx.message.server.roles,
                                                                      name="Group {}".format(groupID)))
                        file['groups'][index]['members'].remove(member)
                        WriteFile('cogs/json/matchmaking.json', file)

                        await self.bot.say(
                            "{} Member ``{}`` removed from the ``{}`` group.".format(ctx.message.author.mention, member,
                                                                                     file['groups'][index]['quest']))
                    except Exception as e:
                        await self.bot.say(
                            "{} Member ``{}`` not found in the ``{}`` group.".format(ctx.message.author.mention, member,
                                                                                     file['groups'][index]['quest']))
                else:
                    await self.bot.say("{} You are not the owner of the group.".format(ctx.message.author.mention))
            else:
                await self.bot.say(
                "{} Group commands must be used in a group channel.".format(ctx.message.author.mention))

def setup(bot):
    bot.add_cog(Group(bot))