from discord.ext import commands
import discord
from discord.ui import Button, View
from discord.utils import get

# Define a setup function to allow the main bot file to register this command
async def setup(bot):
    print("Setting up Duth cog...")
    await bot.add_cog(Other(bot))


class Other(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=["commands", "cmds"])
    async def help(self, ctx):
        #buttons
        style = discord.ButtonStyle.green
        uni = Button(label="CS IHU", style=style, emoji="🏫")
        town = Button(label="KAVALA", style=style, emoji="🏙️")
        bot = Button(label="BOT", style=style, emoji="🤖")

        view = View(timeout=30)
        view.add_item(uni)
        view.add_item(town)
        view.add_item(bot)

        page1 = discord.Embed(
            colour=discord.Colour.blue()
        )
        page1.set_author(name="Commands")
        page1.add_field(name="__CS IHU__", value="**-services** - Εμφανίζει όλες τις υπηρεσίες για το τμήμα.\n"
                                            "**-teachers** - Εμφανίζει πληροφορίες για τους καθηγητές του τμήματος.\n"
                                            "**-map** - Εμφανίζει τον χάρτη για κτήρια τμήματος.\n"
                                            "**-foodclub** - Εμφανίζει τα ωράρια της λέσχης.\n"
                                            "**-contact** - Εμφανίζει τα στοιχεία επικοινωνίας για το τμήμα.\n"
                                            "**-books** - Εμφανίζει την λίστα των βιβλίων των εξαμήνων με τους κωδικούς.\n"
                                            "**-lessons** - Εμφανίζει το πρόγραμμα σπουδών όλων των εξαμήνων.\n"
                                            "**-library** - Εμφανίζει τις ώρες λειτουργίας της βιβλιοθήκης.\n"
                                            "**-studyguide** - Εμφανίζει τον οδηγό σπουδών.\n",
                                            inline=False)
        page2 = discord.Embed(
            colour=discord.Colour.blue()
        )

        page2.add_field(name="__Περί Καβάλας__", value="**-bmap <αριθμός γραμμής>** - Δείχνει την διαδρομή του λεωφορείου.\n"
                                                    "**-telematics <αριθμός στάσης>** - Εμφανίζει την ώρα άφιξης των λεωφορείων.\n", 
                                                    "**-setroute <αριθμός στάσης>** - Αποθηκεύει τον στάση της προτίμησης σας.\n", 
                                                    "**-myroute** - Εμφανίζει τα δρομολόγια της αποθηκευμένης στάσης.",
                                                inline=False)

        page3 = discord.Embed(
            colour=discord.Colour.blue()
        )
        page3.add_field(name="__Bot Info__", value="**-ping** - Εμφανίζει την ταχύτητα του μποτ ανα δευτερόλεπτο.\n"
                                                "**-code** - Στέλνει το link με τον κώδικα από το bot.", inline=False)
        
        message = await ctx.send(embed=page1, view=view)

        async def edit_message_and_defer(interaction, page):
            await message.edit(embed=page)
            await interaction.response.defer()

        async def uni_callback(interaction):
            await edit_message_and_defer(interaction, page1)
        
        async def town_callback(interaction):
            await edit_message_and_defer(interaction, page2)
        
        async def bot_callback(interaction):
            await edit_message_and_defer(interaction, page3)

        uni.callback = uni_callback
        town.callback = town_callback
        bot.callback = bot_callback
'''
    @commands.Cog.listener()
    async def on_message(self, message):
        # Prevent the bot from responding to itself or other bots
        if message.author.bot:
            return

        # List of all bot commands with prefix
        bot_commands = [f"-{alias}" for command in self.bot.commands for alias in [command.name, *command.aliases]]
        
        # Replace with your specific channel IDs
        command_channel_id = 898491436738174999
        info_channel_id = 901068164648030228

        # Check if the message is in the specific channel and matches a bot command
        if message.channel.id == command_channel_id and message.content in bot_commands:
            # Retrieve the information channel
            info_channel = get(self.bot.get_all_channels(), id=info_channel_id)
            if info_channel:
                await message.channel.send(f"Οι εντολές εδώ: {info_channel.mention}")
            return  # Stop further processing if condition is met

        # Process commands as usual
        await self.bot.process_commands(message)
'''
#FIXME: Add the above code to the bot_commands.py file to work for all files