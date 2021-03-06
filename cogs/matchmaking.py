import asyncio
import threading

import discord
from discord.ext import commands

from functions import ReadFile, WriteFile, SearchGroup


class Matchmaking:
    """Matchmaking commands"""

    def __init__(self, bot):
        self.bot = bot
        self.lock = threading.RLock()

    #Registration
    @commands.command(pass_context=True)
    async def reg(self, ctx, *, playerID: str):
        """Register your Player ID and receive full access to the server"""

        with self.lock:
            file = ReadFile('cogs/json/users.json')
            file.update({"{}".format(ctx.message.author.id) : "{}".format(playerID)})
            WriteFile('cogs/json/users.json', file)

            await self.bot.add_roles(ctx.message.author, discord.utils.get(ctx.message.server.roles, name="LFP"))
            await self.bot.say("{} Registered!".format(ctx.message.author.mention))

    @commands.command(pass_context=True)
    async def changePID(self, ctx, *, playerID: str):
        """Changes your Player ID"""

        if ctx.message.server.id == "228244312041848833":
            await self.bot.change_nickname(ctx.message.author, playerID)
            await self.bot.say(":arrow_right: Player ID changed to {}".format(playerID))

    @commands.group(pass_context=True)
    async def lfp(self):
        """Matchmaking commands. Type ``!help lfp`` for more information."""

    @lfp.command(pass_context=True)
    async def help(self, ctx):
        message = "**-> Bot instructions**\n" \
                  "The bot works on a group system. Someone creates a group for a quest, a temporary text channel is cre" \
                  "ated (to allow communication between the group members), and anyone can freely join / leave with a " \
                  "simple command.\n\n" \
                  "**-> Matchmaking commands:**\n" \
                  "!help - Displays help message.\n" \
                  "!lfp create <ship number> <max members> <quest name> - Creates a group for the desired quest\n" \
                  "!lfp join <group ID> - Joins a group (Each group and it's respective ID are in the #groups-board channel)\n" \
                  "!lfp leave <group ID> - Leaves a group\n\n" \
                  "**-> Group commands:** (Must be used in a group channel)\n" \
                  "!group leave - Leaves the group\n\n" \
                  "**-> Group owner commands:** (Must be used in a group channel)\n" \
                  "!group remove <user> - Removes user from your group\n" \
                  "!group finish - Finishes the quest and deletes the channel\n"
        await self.bot.send_message(ctx.message.author, message)

    @commands.cooldown(1, 1.0, commands.BucketType.user)
    @lfp.command(pass_context=True)
    async def create(self, ctx, ship : int, maxmembers : int, *, questname : str):
        """Creates a group."""

        with self.lock:
            users = ReadFile('cogs/json/users.json')
            if ctx.message.author.id in users:
                file = ReadFile('cogs/json/matchmaking.json')

                try:
                    id = file['groups'][-1]['id'] + 1
                except Exception:
                    id = 0

                file['groups'].append({"id" : id, "quest" : questname, "ship" : ship, "owner" : ctx.message.author.id, "members" : [ctx.message.author.id], "maxmembers" : maxmembers})
                if not discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)):
                    await self.bot.create_role(ctx.message.server, name="Group {}".format(id))

                await asyncio.sleep(1)
                await self.bot.add_roles(ctx.message.author, discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)))

                everyone = discord.PermissionOverwrite(read_messages=False)
                mine = discord.PermissionOverwrite(read_messages=True, send_messages=True)

                await self.bot.create_channel(ctx.message.server, 'group-{}'.format(id), (ctx.message.server.default_role, everyone), (discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)), mine))

                WriteFile('cogs/json/matchmaking.json', file)

                message = "@here A group for ``{}`` on Ship {} has been created by ``{}``. Type ``!lfp join {}`` to join!".format(questname, ship, ctx.message.author.nick, id)
                await self.bot.send_message(discord.Object("174958246837223425"), message)
            else:
                await self.bot.say("You are not registered! Type ``!help reg``.")

    @lfp.command(pass_context=True)
    async def join(self, ctx, id : int):
        """Joins a group."""

        with self.lock:
            users = ReadFile('cogs/json/users.json')
            if ctx.message.author.id in users:
                try:
                    file = ReadFile('cogs/json/matchmaking.json')
                    index = SearchGroup(id)

                    if ctx.message.author.id not in file['groups'][index]['members']:
                        try:
                            await self.bot.add_roles(ctx.message.author, discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)))
                            file['groups'][index]['members'].append(ctx.message.author.id)
                            WriteFile('cogs/json/matchmaking.json', file)

                            await self.bot.say("{} Joined the ``{}`` group, owned by ``{}``.".format(ctx.message.author.mention, file['groups'][index]['quest'], users[file['groups'][index]['owner']]))

                        except Exception as e:
                            await self.bot.say("{} Could not find the requested group. Please check the #group-board channel.".format(ctx.message.author.mention))
                    else:
                        await self.bot.say("{} You are already in that group.".format(ctx.message.author.mention))
                except:
                    await self.bot.say("{} Could not find a group with that ID. Check #groups-board for the right ID.".format(ctx.message.author.mention))
            else:
                await self.bot.say("You are not registered! Type ``!help reg``.")

    @lfp.command(pass_context=True)
    async def leave(self, ctx, id : int):
        """Leaves the selected group."""

        with self.lock:
            file = ReadFile('cogs/json/matchmaking.json')
            index = SearchGroup(id)

            if ctx.message.author.id in file['groups'][index]['members']:
                await self.bot.remove_roles(ctx.message.author, discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)))

                file['groups'][index]['members'].remove(ctx.message.author.id)

                WriteFile('cogs/json/matchmaking.json', file)

                await self.bot.say("{} You have been removed from the ``{}`` group.".format(ctx.message.author.mention, file['groups'][id]['quest']))
            else:
                await self.bot.say("{} You are not in that group.".format(ctx.message.author.mention))

    @lfp.command(pass_context=True)
    async def remove(self, ctx, member : str):
        """Removes a selected member from a group. GROUP OWNER ONLY"""

        with self.lock:
            file = ReadFile('cogs/json/matchmaking.json')
            index = SearchGroup(id)

            if ctx.message.author.id == file['groups'][index]['owner']:
                try:
                    await self.bot.remove_roles(ctx.message.server.get_member(member), discord.utils.get(ctx.message.server.roles, name="Group {}".format(id)))
                    file['groups'][index]['members'].remove(member)
                    WriteFile('cogs/json/matchmaking.json', file)

                    await self.bot.say("{} Member ``{}`` removed from the ``{}`` group.".format(ctx.message.author.mention, member, file['groups'][index]['quest']))
                except Exception as e:
                    await self.bot.say("{} Member ``{}`` not found in the ``{}`` group.".format(ctx.message.author.mention, member, file['groups'][index]['quest']))
            else:
                await self.bot.say("{} You are not the owner of the group.".format(ctx.message.author.mention))

def setup(bot):
    bot.add_cog(Matchmaking(bot))