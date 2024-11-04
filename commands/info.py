from discord.ext import commands
import discord

# Define a setup function to allow the main bot file to register this command
async def setup(bot):
    print("Setting up Duth cog...")
    await bot.add_cog(Info(bot))

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"{round(self.bot.latency * 800)}ms")


    @commands.command()
    async def code(self, ctx):
        e = discord.Embed(
            title=":robot: __Bot Code__ :robot:",
            colour=discord.Colour.blue()
        )
        e.add_field(name="Github | Feel free to contribute", value="https://github.com/SteliosGee/ihu_bot", inline=False)
        await ctx.send(embed=e)
