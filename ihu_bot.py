import discord
from discord.ext import commands
from discord.ui import Button, View
from discord import app_commands
import asyncio
from discordtoken import TOKEN
import json
import pandas as pd
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='-', intents=intents)
bot.remove_command('help')


@bot.event
async def on_ready():
    await bot.change_presence(activity=discord.Game(f"-help"))
    await bot.tree.sync(guild=discord.Object(id=898491436738174996))
    print("Bot is ready.")



# ------------------------ IHU INFO ------------------------ #

@bot.command()
async def teachers(ctx):
    with open("teachers.json", "rb") as f:
            teachers = json.load(f)
    e = discord.Embed(
        title=":bookmark_tabs: __Teachers info__ :bookmark_tabs:",
        colour=discord.Colour.red()
    )
    border = ""
    for i in range(1, len(teachers) + 1):
        border += str(i) + ". " + teachers[str(i)]["name"][2:-2] + "\n"
    e.add_field(name="Γράψε τον αριθμό του καθηγητή",
                value=border)
    await ctx.send(embed=e)
    check = lambda m: m.author == ctx.author
    msg = await bot.wait_for('message', check=check, timeout=30)
    try:
        e1 = discord.Embed(
                title=teachers[msg.content]["name"],
                colour=discord.Colour.orange()
            )
        e1.add_field(name="Email", value=teachers[msg.content]["email"], inline=False)
        e1.add_field(name="Τηλέφωνο", value=teachers[msg.content]["phone"], inline=False)
        e1.add_field(name="Ώρες Διαθεσιμότητας", value=teachers[msg.content]["hours"], inline=False)
        await ctx.send(embed=e1)
    except:
        await ctx.send("Γράψε έναν έγκυρο αριθμό")



@bot.command()
async def services(ctx):
    e = discord.Embed(
        title=":placard: __CS IHU Υπηρεσίες__ :placard:",
        colour=discord.Colour.orange()
    )
    e.add_field(name='Ιστοσελίδα Τμήματος Πληροφορικής', value='http://www.cs.ihu.gr\n', inline=False)
    e.add_field(name='Εγγραφή στο uregister', value='https://uregister.emt.ihu.gr/\n', inline=False)
    e.add_field(name='Ξέχασα τον κωδικό μου', value='https://mypassword.emt.ihu.gr/\n', inline=False)
    e.add_field(name='Ηλεκτρονική Γραμματεία', value='https://uniportal.ihu.gr/\n', inline=False)
    e.add_field(name='Αίτηση απόκτησης ακαδημαϊκής ταυτότητας', value='https://academicid.minedu.gov.gr/\n', inline=False)
    e.add_field(name='Υπηρεσία δήλωσης συγγραμάτων', value='https://eudoxus.gr/\n', inline=False)
    e.add_field(name='Ανοικτά μαθήματα (open courses)', value='https://opencourses.gr/\n', inline=False)
    e.add_field(name='Πλατφόρμα ασύγχρονης εκπαίδευσης', value='https://moodle.cs.ihu.gr\n', inline=False)
    e.add_field(name='Διαχείριση ομάδων μαθημάτων', value='https://courses.cs.ihu.gr/\n', inline=False)
    e.add_field(name='Φοιτητική μέριμνα', value='http://www.teikav.edu.gr/portal/index.php/el/home/students/student-care\n', inline=False)
    await ctx.send(embed=e)


@bot.command()
async def books(ctx):

    books = pd.read_csv('books.csv')

    pages = []
    TOTAL_PAGES = 3
    for i in range(0, TOTAL_PAGES):
        semester = i+1
        filtered_books = books[books['semester'] == semester]
        filtered_books = filtered_books[['subject','code']]
        page = discord.Embed (
            title = f"__{i+1}ο Εξάμηνο__",
            colour = discord.Colour.orange()
        )
        for i in range(0, len(filtered_books)):
            page.add_field(name = filtered_books['subject'].iloc[i], value = filtered_books['code'].iloc[i], inline = False)
        pages.append(page)

    message = await ctx.send(embed = pages[0])

    reactions = ['⏮', '◀', '▶', '⏭']
    for reaction in reactions:
        await message.add_reaction(reaction)

    def check(reaction, user):
        return user == ctx.author

    reaction = None
    i = 0
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
        except:
            break
        if str(reaction) == '⏮':
            i = 0
            await message.edit(embed = pages[i])
        elif str(reaction) == '◀':
            if i > 0:
                i -= 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '▶':
            if i < 2:
                i += 1
                await message.edit(embed = pages[i])
        elif str(reaction) == '⏭':
            i = 2
            await message.edit(embed = pages[i])
        

    await message.clear_reactions()


@bot.command()
async def lessons(ctx):
    lessons = pd.read_csv('lessons.csv')
    pages = []
    TOTAL_PAGES = 8
    for i in range(0, TOTAL_PAGES):
        semester = i+1
        filtered_lessons = lessons[lessons['semester'] == semester]
        filtered_lessons = filtered_lessons[['subject','credits', 'teaching_hours', 'subject_type']]
        page = discord.Embed (
            title = f"__{i+1}ο Εξάμηνο__",
            colour = discord.Colour.orange()
        )
        for i in range(0, len(filtered_lessons)):
            page.add_field(name = filtered_lessons['subject'].iloc[i], 
                           value = "Διδακτικές Μονάδες: " + str(filtered_lessons['credits'].iloc[i]) +'\n'+
                                   "Ώρες Διδασκαλίας: " + str(filtered_lessons['teaching_hours'].iloc[i]) +'\n'+
                                   "Τύπος Μαθήματος: " + filtered_lessons['subject_type'].iloc[i], inline = False)
        pages.append(page)                                            

    message = await ctx.send(embed = pages[0])

    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']
    
    for reaction in reactions:
        await message.add_reaction(reaction)
    

    def check(reaction, user):
        return user == ctx.author

    i = 0
    reaction = None
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=30.0, check=check)
            await message.remove_reaction(reaction, user)
            if str(reaction) in reactions:
                i = reactions.index(str(reaction))
                await message.edit(embed=pages[i])
        except:
            break
    await message.clear_reactions()


@bot.command()
async def map(ctx):
    e = discord.Embed(
        color=discord.Colour.orange()
    )
    e.set_image(url="https://i.postimg.cc/pdr8kyFq/map.png")
    await ctx.send(embed=e)


@bot.command()
async def foodclub(ctx):
    e = discord.Embed(
        title=":fork_and_knife: __Ωράρια Λέσχης__ :fork_and_knife:",
        colour=discord.Colour.blue()
    )
    e.add_field(name="__Πρωί__", value="8:00-9:30", inline=True)
    e.add_field(name="__Μεσημέρι__", value="12:30-16:00", inline=True)
    e.add_field(name="__Βράδυ__", value="18:00-21:00", inline=True)
    await ctx.send(embed=e)


@bot.command(aliases=["secretariat", "contact"])
async def secreteriat(ctx):
    e = discord.Embed(
        title=":telephone: __Γραμματεία__ :telephone:",
        colour=discord.Colour.red()
    )
    e.add_field(name="__Ώρες Γραφείου__", value="11:00-13:00", inline=False)
    e.add_field(name="__Email__", value="info@cs.ihu.gr", inline=False)
    e.add_field(name="__Τηλέφωνα__", value="2510462147\n2510462341", inline=False)
    e.add_field(name="Website", value="http://www.cs.ihu.gr", inline=False)
    await ctx.send(embed=e)


@bot.command()
async def library(ctx):
    e = discord.Embed(
        title=":books: __Βιβλιοθήκη__ :books:",
        colour=discord.Colour.green()
    )
    e.add_field(name="__Ώρες Λειτουργίας__", value="8:00-14:30", inline=False)
    await ctx.send(embed=e)

# ----------------------------- KAVALA ----------------------------- #

@bot.command()
async def bmap(ctx, arg=None):
    error_line = f"Η γραμμή {arg} δεν λειτουργεί"
    busses = ['https://i.postimg.cc/y6SmmMxK/Capture.jpg', error_line, error_line, "https://i.postimg.cc/y6SmmMxK/Capture.jpg", "https://i.postimg.cc/G3ZZznjx/Capture.jpg", error_line, error_line,
                error_line, error_line, "https://i.postimg.cc/kMtH2hd6/Capture.jpg", "https://i.postimg.cc/dVnHbbGX/Capture.jpg"]
    if arg==None:
        await ctx.send("Γράψε την γράμμη μετά την εντολή `π.χ. -bmap 5`")
    else:
        try:
            if busses[int(arg)-1]!=error_line:
                e = discord.Embed(
                color=discord.Color.orange()
            )
                e.set_image(url=busses[int(arg)-1])
                await ctx.send(embed=e)
            else:
                await ctx.send(error_line)
        except:
            await ctx.send("Γράψε μια έγκυρη γραμμή")

    
# ----------------------------- COMPUTER SCIENCE ----------------------------- #

@bot.command()
async def dec(ctx, arg):
    e = discord.Embed(
        colour=discord.Colour.red()
    )
    e.add_field(name=f"__Decimal number: {arg}__", value=f"**Binary number: {bin(int(arg))[2:]}\n"
                                                        f"Octal number: {oct(int(arg))[2:]}\n"
                                                        f"Hexadecimal: {hex(int(arg))[2:]}**")
    await ctx.send(embed=e)


@bot.command(aliases=["bin"])
async def _bina(ctx, arg):
    e = discord.Embed(
        colour=discord.Colour.red()
    )
    decimal = int(arg, 2)
    e.add_field(name=f"__Binary number: {arg}__", value=f"**Decimal number: {decimal}\n"
                                                        f"Octal number: {oct(int(decimal))[2:]}\n"
                                                        f"Hexadecimal: {hex(int(decimal))[2:]}**")
    await ctx.send(embed=e)


@bot.command()
async def asc(ctx, arg):
    e = discord.Embed(
        colour=discord.Colour.red()
    )
    e.add_field(name=f"__Value: {arg}__", value=f"**ASCII value: {ord(arg)}\n**")
    await ctx.send(embed=e)

@bot.command()
async def ascrev(ctx, arg):
    e = discord.Embed(
        colour=discord.Colour.red()
    )
    e.add_field(name=f"__ASCII value: {arg}__", value=f"**Actual value: {chr(int(arg))}\n**")
    await ctx.send(embed=e)

@bot.command()
async def color(ctx, arg):
    arg = arg.lower()
    colors = {'white':['White', '#FFFFFF', (255, 255, 255)], 'silver':['Silver', '#C0C0C0', (192, 192, 192)],
                'gray':['Gray', '#808080', (128, 128, 128)], 'black':['Black', '#000000', (0, 0, 0)],
                'red':['Red', '#FF0000', (255, 0, 0)], 'maroon':['Maroon', '#800000', (128, 0, 0)],
                'yellow':['Yellow', '#FFFF00', (255, 255, 0)], 'olive':['Olive', '#800000', (128, 128, 0)],
                'lime':['Lime', '#00FF00', (0, 255, 0)], 'green':['Green', '#008000', (0, 128, 0)],
                'aqua':['Aqua', '#00FFFF', (0, 255, 255)], 'teal':['Teal', '#008080', (0, 128, 128)],
                'blue':['Blue', '#0000FF', (0, 0, 255)], 'navy':['Navy', '#000080', (0, 0, 128)],
                'fuchsia':['Fuchsia', '#FF00FF', (255, 0, 255)], 'purple':['Purple', '#800080', (128, 0, 128)]}
    e = discord.Embed(
        title = f"__{colors[arg][0]}__",
        color = discord.Color.from_rgb(*colors[arg][2])
    )
    e.add_field(name="HEX CODE", value=f"{colors[arg][1]}", inline=True)
    e.add_field(name="RGB CODE", value=f"{colors[arg][2]}", inline=True)
    await ctx.send(embed=e)

@bot.command()
async def colorlist(ctx):
    e = discord.Embed(
        title="__COLORS__",
        color=discord.Color.random()
    )
    colors = ["white", "silver", "gray", "black", "red", "maroon", "yellow", "olive", "lime", "green", "aqua", 
                "teal", "blue", "navy", "fuchsia", "purple"]
    inline = False
    for i in colors:
        e.add_field(name=f"● {str(i)}", value='\u200b', inline=True)
    await ctx.send(embed=e)

@bot.command()
async def ping(ctx):
    await ctx.send(f"{round(bot.latency * 800)}ms")


#----------------------------- HELP -----------------------------#

@bot.command(aliases=["help", "commands", "cmds"])
async def _help(ctx):
    #buttons
    style = discord.ButtonStyle.green
    uni = Button(label="CS IHU", style=style, emoji="🏫")
    town = Button(label="KAVALA", style=style, emoji="🏙️")
    comp = Button(label="COMPUTER SCIENCE", style=style, emoji="💻")
    bot = Button(label="BOT", style=style, emoji="🤖")

    view = View(timeout=30)
    view.add_item(uni)
    view.add_item(town)
    view.add_item(comp)
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
                                         "**-secreteriat** - Εμφανίζει τις επικοινωνίες με γραμματεία.\n"
                                         "**-library** - Εμφανίζει τις ώρες λειτουργίας της βιβλιοθήκης.",
                                         inline=False)
    page2 = discord.Embed(
        colour=discord.Colour.blue()
    )

    page2.add_field(name="__Περί Καβάλας__", value="**-bmap <αριθμός γραμμής>** - Δείχνει την διαδρομή του λεωφορείου.", inline=False)

    page3 = discord.Embed(
        colour=discord.Colour.blue()
    )                     
    page3.add_field(name="__Περί πληροφορικής__",
                value="**-bin <δυαδικός αιρθμός>** - Μετατρέπει τον δυαδικό αριθμό σε δεκαδικό, "
                      "οκταδικό και δεκαεξαδικό.\n"
                      "**-dec <δεκαδικός αριθμός>** - Μετατρέπει τον δεκαδικό αριθμό σε δυαδικό, "
                      "οκταδικό και δεκαεξαδικό.\n"
                      "**-asc <χαρακτήρας>** - Δείχνει την ASCII τιμή του χαρακτήρα.\n"
                      "**-ascrev <αριθμός>** - Δείχνει τον χαρακτήρα που αντιπροσωπεύει η ASCII τιμή.\n"
                      "**-color <χρώμα>** - Εμφανίζει τον HEX και RGB κώδικα του χρώματος.\n"
                      "**-colorlist** - Εμφανίζει την λίστα βασικών χρωμάτων.", inline=False)

    page4 = discord.Embed(
        colour=discord.Colour.blue()
    )
    page4.add_field(name="__Bot Info__", value="**-ping** - Εμφανίζει την ταχύτητα του μποτ ανα δευτερόλεπτο.", inline=False)
    
    message = await ctx.send(embed=page1, view=view)

    async def uni_callback(interaction):
        await message.edit(embed=page1)
        await interaction.response.send_message("Εντολές σχετικά με το πανεπιστήμιο", ephemeral=True, delete_after=3)

    
    async def town_callback(interaction):
        await message.edit(embed=page2)
        await interaction.response.send_message("Εντολές σχετικά με την πόλη", ephemeral=True, delete_after=3)

    async def comp_callback(interaction):
        await message.edit(embed=page3)
        await interaction.response.send_message("Εντολές σχετικά με την πληροφορική", ephemeral=True, delete_after=3)
    
    async def bot_callback(interaction):
        await message.edit(embed=page4)
        await interaction.response.send_message("Εντολές σχετικά με το μποτ", ephemeral=True, delete_after=3)

    uni.callback = uni_callback
    town.callback = town_callback
    comp.callback = comp_callback
    bot.callback = bot_callback
    

#------------------------------------------------------------Test Code------------------------------------------------------------


"""
@bot.tree.command(name = "help", description = "Testing mode", guild=discord.Object(id=898491436738174996)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction):
    await interaction.response.send_message("Hello!")
"""
bot.run(TOKEN)
