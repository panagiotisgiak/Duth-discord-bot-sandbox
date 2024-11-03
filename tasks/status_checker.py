import discord
from utils.helpers import check_server_status, save_message_id, load_message_id
import config
import datetime
import asyncio
import os
import json





async def check_duth_status(bot):
    await bot.wait_until_ready()
    channel = bot.get_channel(config.STATUS_CHECK_CHANNEL_ID)

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
    e.add_field(name="Τελευταίος Έλεγχος", value="Ποτέ", inline=False)

    # Load the existing message ID if available
    message_id = await load_message_id()

    # Check if a previous message exists, otherwise send a new message
    if message_id:
        try:
            message = await channel.fetch_message(message_id)
        except discord.NotFound:
            # Message no longer exists; send a new one
            message = await channel.send(embed=e)
            await save_message_id(message.id)
    else:
        # No previous message; send a new one
        message = await channel.send(embed=e)
        await save_message_id(message.id)

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
            green_boxes = "🟩 " * status_counts[server_name]['up']  # Green boxes for uptime
            red_boxes = "🟥 " * status_counts[server_name]['down']  # Red boxes for downtime
            
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
            server_index = list(servers.keys()).index(server_name)
            if server_index < len(e.fields):
                e.set_field_at(server_index, name=server_name, value=status_message, inline=False)
            else:
                e.add_field(name=server_name, value=status_message, inline=False)

        # Update the last update time field
        current_time = datetime.datetime.now().strftime("%H:%M:%S\n%Y-%m-%d")
        e.set_field_at(len(servers), name="Τελευταίος Έλεγχος", value=current_time, inline=False)

        # Edit the existing message with the updated embed
        await message.edit(embed=e)
        
        await asyncio.sleep(300)  # Sleep for 5 minutes
