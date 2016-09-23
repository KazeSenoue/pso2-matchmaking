import threading

import discord
from discord.ext import commands

from functions import ReadFile, WriteFile, SearchGroup, SearchMember
from .utils import checks


class Moderation:
    """Mod only commands"""

    def __init__(self, bot):
        self.bot = bot
        self.lock = threading.RLock()

    @checks.mod_or_permissions(manage_messages=True, no_pm=True)
    @commands.command(pass_context=True)
    async def finish(self, ctx, groupID : int):
        """Finishes a group."""

        with self.lock:
            index = SearchGroup(groupID)
            file = ReadFile('cogs/json/matchmaking.json')

            server = ctx.message.server
            for user in file['groups'][index]['members']:
                await self.bot.remove_roles(server.get_member(user),
                                            discord.utils.get(server.roles, name="Group {}".format(groupID)))

            await self.bot.delete_channel(
                discord.utils.get(server.channels, name="group-{}".format(groupID)))
            await self.bot.delete_role(server,
                                       discord.utils.get(server.roles, name="Group {}".format(groupID)))

            file['groups'].pop(index)

            WriteFile('cogs/json/matchmaking.json', file)

    @checks.mod_or_permissions(manage_messages=True, no_pm=True)
    @commands.command(pass_context=True)
    async def remove(self, ctx, groupID : int, *, membername : str):
        """Remove a member from a group."""

        with self.lock:
            file = ReadFile('cogs/json/matchmaking.json')
            id = SearchGroup(groupID)

            try:
                member = SearchMember(membername)

                await self.bot.remove_roles(ctx.message.server.get_member(member), discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)))
                file['groups'][id]['members'].remove(member)
                WriteFile('cogs/json/matchmaking.json', file)

                await self.bot.say("{} Member ``{}`` removed from the ``{}`` group.".format(ctx.message.author.mention, membername, file['groups'][id]['quest']))
            except Exception as e:
                await self.bot.say("{} Member ``{}`` not found in the ``{}`` group.".format(ctx.message.author.mention, membername, file['groups'][id]['quest']))

def setup(bot):
    bot.add_cog(Moderation(bot))