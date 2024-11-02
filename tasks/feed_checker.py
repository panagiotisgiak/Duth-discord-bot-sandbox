import feedparser
import discord
from utils.helpers import load_last_guid, save_last_guid
import config
import asyncio

async def check_feed(bot):
    channel = bot.get_channel(config.DUTH_CHANNEL_ID)
    last_guid = load_last_guid()
    while True:
        feed = feedparser.parse(config.RSS_URL)
        if feed.entries and feed.entries[0].guid != last_guid:
            last_guid = feed.entries[0].guid
            save_last_guid(last_guid)
            e = discord.Embed(
                title=f":newspaper: {feed.entries[0].title}",
                description=feed.entries[0].description[:300] + "...",
                url=feed.entries[0].link,
                colour=discord.Colour.blue()
            )
            await channel.send(embed=e)
        await asyncio.sleep(300)
