import discord
from discord.ext import commands, tasks
import config

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.status_index = 0

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.rotate_status.is_running():
            self.rotate_status.start()
        print(f'General Cog: Bot logado como {self.bot.user.name}')

    @tasks.loop(seconds=15)
    async def rotate_status(self):
        activity = config.STATUS_LIST[self.status_index]
        await self.bot.change_presence(activity=activity)
        self.status_index = (self.status_index + 1) % len(config.STATUS_LIST)

    @rotate_status.before_loop
    async def before_rotate_status(self):
        await self.bot.wait_until_ready()

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx):
        await self.bot.tree.sync()
        await ctx.send("Comandos sincronizados!")

async def setup(bot):
    await bot.add_cog(General(bot))
