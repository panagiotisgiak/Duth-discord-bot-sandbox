import discord
from discord.ext import commands
from discord.utils import get
from discord.ui import Button, View
import asyncio
from discordtoken import TOKEN
import json
import pandas as pd
import os
import feedparser
import requests
import datetime

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
    if not is_local:
        print("Starting background tasks...")
        bot.loop.create_task(check_feed())
        bot.loop.create_task(check_duth_status())
    else:
        print("Running locally. Background tasks not started.")

#Check if the bot is running locally or on server
def is_local():
    if os.getenv('RUNNING_ENV') == 'local':
        return True
    return False

# ------------------------ DUTH STATUS ------------------------ #
def check_server_status(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            return True, "Server is up and running"  # Server is up
    except requests.ConnectionError:
        return False, "Server is not reachable"  # Server is not reachable
    except requests.Timeout:
        return False, "Request timed out"  # Request timed out
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return False, f"An error occurred: {e}"  # General request error
    return False, "Server is down"  # Server is down

async def check_duth_status():
    await bot.wait_until_ready()
    channel = bot.get_channel(1299804831330078722)  # Replace with your channel ID

    # Create the initial embed message
    e = discord.Embed(
        title=":satellite: __DUTH Status__ :satellite:",
        colour=discord.Colour.blue()
    )
    e.set_footer(text="Ελέγχεται κάθε 5 λεπτά.")

    # URLs and their display names
    servers = {
        "CS DUTH": "https://www.cs.duth.gr/",
        "UNISTUDENTS": "https://students.duth.gr/",
        "MOODLE": "https://moodle.cs.duth.gr/",
        "COURSES": "https://courses.cs.duth.gr/"
    }
    
    # Initialize status counts for each server
    status_counts = {name: {'up': 0, 'down': 0} for name in servers.keys()}

    # Add initial status fields for each server
    for server_name in servers.keys():
        e.add_field(name=server_name, value="Waiting for the first status check...", inline=False)

    # Add a field for the last update time
    e.add_field(name="Last Update Time", value="Never", inline=False)

    message = await channel.send(embed=e)

    while True:
        # Check the status of each server
        for server_name, url in servers.items():
            server_up, status_message = check_server_status(url)

            if server_up:
                # Reset down count and increment up count
                status_counts[server_name]['down'] = 0
                status_counts[server_name]['up'] += 1
            else:
                # Reset up count and increment down count
                status_counts[server_name]['up'] = 0
                status_counts[server_name]['down'] += 1

            # Build the status message with green and red boxes
            green_boxes = "🟩 " * status_counts[server_name]['up']  # Green boxes for the server being up
            red_boxes = "🟥 " * status_counts[server_name]['down']  # Red boxes for the server being down
            
            # Limit the boxes to a maximum of 20
            total_boxes = (green_boxes + red_boxes).strip()
            if len(total_boxes) > 20:
                total_boxes = total_boxes[-20:]  # Keep only the last 20 boxes

            # Update the status message based on server status
            if server_up:
                status_message = "Server is up and running"
            else:
                status_message = status_message  # Use the specific error message
            
            # Construct the final message
            status_message = f"{total_boxes}\n{status_message}"

            # Update the status field in the embed
            e.set_field_at(list(servers.keys()).index(server_name), name=server_name, value=status_message, inline=False)

        # Update the last update time field
        current_time = datetime.datetime.now().strftime("%H:%M:%S\n%Y-%m-%d")
        e.set_field_at(len(servers), name="Τελευταίος Έλεγχος", value=current_time, inline=False)

        # Edit the existing message with the updated embed
        await message.edit(embed=e)
        
        await asyncio.sleep(300)  # Sleep for 5 minutes



# ------------------------ DUTH ANNOUNCEMENTS ------------------------ #

CHANNEL_ID = 901044939113254913

rss_url = "https://cs.duth.gr/webresources/feed.xml"
last_guid = None

def load_last_guid():
    if os.path.exists("last_guid.txt"):
        with open("last_guid.txt", "r") as f:
            return f.read().strip()
    return None


def save_last_guid(guid):
    with open("last_guid.txt", "w") as f:
        f.write(guid)


last_guid = load_last_guid()

async def check_feed():
    global last_guid
    await bot.wait_until_ready()
    channel = bot.get_channel(CHANNEL_ID)

    while True:
        feed = feedparser.parse(rss_url)
        if feed.entries:
            latest_entry = feed.entries[0]
            if latest_entry.guid != last_guid:
                last_guid = latest_entry.guid
                save_last_guid(last_guid)
                e = discord.Embed(
                    title=f":newspaper: {latest_entry.title}",
                    description=latest_entry.description[:300] + "..." if len(latest_entry.description) > 300 else latest_entry.description,
                    url=latest_entry.link,
                    colour=discord.Colour.blue()
                )
                e.set_footer(text="Πηγή: Τμήμα Πληροφορικής, ΔΠΘ")
                await channel.send(embed=e)
        await asyncio.sleep(300)

# ------------------------ DUTH INFO ------------------------ #

@bot.command()
async def teachers(ctx):

    with open("ihu_data/teachers.json", "rb") as f:
            teachers = json.load(f)

    e = discord.Embed(
        title=":bookmark_tabs: __Πληροφορίες Καθηγητών__ :bookmark_tabs:",
        colour=discord.Colour.red()
    )
    border = ""
    for i in range(1, len(teachers) + 1):
        border += str(i) + ". " + teachers[str(i)]["name"] + "\n"
    e.add_field(name="Γράψε τον αριθμό του καθηγητή", value=border)
    await ctx.send(embed=e)

    check = lambda m: m.author == ctx.author
    msg = await bot.wait_for('message', check=check, timeout=30)

    try:
        teacher_index = int(msg.content)
        if str(teacher_index) in teachers:
            teacher_info = teachers[str(teacher_index)]
            response = (
                f"**Email:** {teacher_info['email']}\n"
                f"**Τηλέφωνο:** {teacher_info['phone']}\n"
                f"**Ώρες Διαθεσιμότητας:** {teacher_info['hours']}"
            )
            await ctx.send(embed=discord.Embed(
                title=f"__{teacher_info['name']}__",
                description=response,
                colour=discord.Colour.orange()
            ))
        else:
            await ctx.send("Δεν υπάρχει καθηγητής με αυτόν τον αριθμό.")
    except ValueError:
        await ctx.send("Δώσε έναν έγκυρο αριθμό.")




@bot.command()
async def services(ctx):

    services = pd.read_csv('ihu_data/services.csv')

    e = discord.Embed(
        title=":placard: __CS IHU Υπηρεσίες__ :placard:",
        colour=discord.Colour.orange()
    )
    for i in range(0, len(services)):
        e.add_field(name = services['service'].iloc[i], value = services['link'].iloc[i], inline = False)
    await ctx.send(embed=e)


@bot.command()
async def books(ctx):

    books = pd.read_csv('ihu_data/books.csv')

    pages = []
    TOTAL_PAGES = 7
    for i in range(0, TOTAL_PAGES):
        semester = i+1
        filtered_books = books[books['semester'] == semester]
        filtered_books = filtered_books[['subject','code']]
        page = discord.Embed (
            title = f"__{i+1}ο Εξάμηνο__",
            description="__Κωδικοί Συγγραμάτων__",
            colour = discord.Colour.orange()
        )
        for i in range(0, len(filtered_books)):
            page.add_field(name = filtered_books['subject'].iloc[i], value = filtered_books['code'].iloc[i], inline = False)
        page.set_footer(text = "Link για τις δηλώσεις: https://service.eudoxus.gr/student")
        pages.append(page)
    
    roles = ['1ο Έτος', '2ο Έτος', '3ο Έτος', '4ο Έτος']
    highestRole = -1

    for i, role in enumerate(roles):
        if discord.utils.get(ctx.guild.roles, name=role) in ctx.author.roles:
            highestRole = i

    if highestRole > -1:
        pageindex = highestRole * 2
        message = await ctx.send(embed=pages[pageindex])
    else:
        message = await ctx.send(embed=pages[0])
        pageindex = 0

    reactions = ['⏮', '◀', '▶', '⏭']
    for reaction in reactions:
        await message.add_reaction(reaction)

    def check(reaction, user):
        return user == ctx.author

    reaction = None
    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout = 30.0, check = check)
            await message.remove_reaction(reaction, user)
            
            if str(reaction) == '⏮':
                pageindex = 0
                await message.edit(embed = pages[pageindex])
            elif str(reaction) == '◀':
                if pageindex > 0:
                    pageindex -= 1
                    await message.edit(embed = pages[pageindex])
            elif str(reaction) == '▶':
                if pageindex < TOTAL_PAGES - 1:
                    pageindex += 1
                    await message.edit(embed = pages[pageindex])
            elif str(reaction) == '⏭':
                pageindex = TOTAL_PAGES - 1
                await message.edit(embed = pages[pageindex])
        except asyncio.TimeoutError:
            break
        
    await message.clear_reactions()

@bot.command()
async def lessons(ctx):

    lessons = pd.read_csv('ihu_data/lessons.csv')

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
            page.add_field(name = "`" + filtered_lessons['subject'].iloc[i] + "`", 
                           value = "Διδακτικές Μονάδες: " + str(filtered_lessons['credits'].iloc[i]) +'\n'+
                                   "Ώρες Διδασκαλίας: " + str(filtered_lessons['teaching_hours'].iloc[i]) +'\n'+
                                   "Τύπος Μαθήματος: " + filtered_lessons['subject_type'].iloc[i], inline = True)
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


# @bot.command()
# async def map(ctx):
#     # send image without embed
#     file = discord.File("map.jpg", filename="map.jpg")
#     e = discord.Embed(
#         title=":map: __Χάρτης Τμήματος__ :map:",
#         colour=discord.Colour.blue()
#     )
#     e.set_image(url="attachment://map.jpg")
#     await ctx.send(file=file, embed=e)
#     #TODO: Add buttons for useful buildings and professors' offices



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


@bot.command()
async def studyguide(ctx):
    e = discord.Embed(
        title=":books: __Οδηγός Σπουδών__ :books:",
        colour=discord.Colour.green()
    )
    e.add_field(name="__Link__", value="https://cs.ihu.gr/cs_hosting/attachments/webpages/el_study_guide.pdf", inline=False)
    await ctx.send(embed=e)

# ----------------------------- BOT ----------------------------- #

@bot.command()
async def ping(ctx):
    await ctx.send(f"{round(bot.latency * 800)}ms")

@bot.command()
async def code(ctx):
    e = discord.Embed(
        title=":robot: __Bot Code__ :robot:",
        colour=discord.Colour.blue()
    )
    e.add_field(name="Github", value="https://github.com/PhoenixDoom/ihu_bot", inline=False)
    await ctx.send(embed=e)


#----------------------------- HELP -----------------------------#

@bot.command(aliases=["commands", "cmds"])
async def help(ctx):
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

    page2.add_field(name="__Περί Καβάλας__", value="**-bmap <αριθμός γραμμής>** - Δείχνει την διαδρομή του λεωφορείου.", inline=False)

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
    

#------------------------------------------------------------Events------------------------------------------------------------

@bot.event
async def on_message(message):
    bot_commands = [f"-{alias}" for command in bot.commands for alias in [command.name, *command.aliases]]
    if message.channel.id == 898491436738174999 and message.content in bot_commands:
        channel = get(bot.get_all_channels(), id=901068164648030228)
        await message.channel.send(f"Οι εντολές εδώ: {channel.mention}")
        return
    await bot.process_commands(message)

#------------------------------------------------------------Test Code------------------------------------------------------------


"""
@bot.tree.command(name = "help", description = "Testing mode", guild=discord.Object(id=898491436738174996)) #Add the guild ids in which the slash command will appear. If it should be in all, remove the argument, but note that it will take some time (up to an hour) to register the command if it's for all guilds.
async def first_command(interaction):
    await interaction.response.send_message("Hello!")
"""
bot.run(TOKEN)
