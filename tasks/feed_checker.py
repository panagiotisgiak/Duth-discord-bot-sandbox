import feedparser
import discord
from utils.helpers import load_last_guid, save_last_guid
import config
import asyncio

async def check_feed(bot):
    channel = bot.get_channel(config.DUTH_CHANNEL_ID)
    last_guid = load_last_guid()
    print(f"Loaded last GUID: {last_guid}")  # Debug print
    while True:
        feed = feedparser.parse(config.RSS_URL)
        if feed.entries:
            current_guid = feed.entries[0].guid
            print(f"Current GUID: {current_guid}")  # Debug print
            if current_guid != last_guid:
                last_guid = current_guid
                save_last_guid(last_guid)
                print(f"Saved new GUID: {last_guid}")  # Debug print
                e = discord.Embed(
                    title=f":newspaper: {feed.entries[0].title}",
                    description=feed.entries[0].description[:300] + "...",
                    url=feed.entries[0].link,
                    colour=discord.Colour.blue()
                )
                await channel.send(embed=e)
            else:
                print("No new GUID found.")  # Debug print
        await asyncio.sleep(300)