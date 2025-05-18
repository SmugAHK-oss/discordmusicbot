import discord
from discord.ext import commands
import yt_dlp
import asyncio

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Set yt-dlp options with cookies-from-browser
ydl_opts = {
    'format': 'bestaudio/best',
    'quiet': True,
    'default_search': 'ytsearch',
    'noplaylist': True,
    'cookiefile': None,
    'cookiesfrombrowser': ('chrome',),  # Or use ('firefox',), etc.
}

ffmpeg_options = {
    'options': '-vn'
}

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user.name}")

@bot.command(name='join')
async def join(ctx):
    if ctx.author.voice:
        await ctx.author.voice.channel.connect()
        await ctx.send(f"Joined {ctx.author.voice.channel}")
    else:
        await ctx.send("You are not in a voice channel.")

@bot.command(name='leave')
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()
        await ctx.send("Left the voice channel.")

@bot.command(name='play')
async def play(ctx, *, search: str):
    if not ctx.voice_client:
        await ctx.send("I'm not in a voice channel. Use `!join` first.")
        return

    await ctx.send(f"Searching for: {search}")
    
    try:
        # Use yt-dlp with browser cookies
        with yt_dlp.YoutubeDL({
            **ydl_opts,
            'cookiesfrombrowser': ('chrome',),
        }) as ydl:
            info = ydl.extract_info(search, download=False)
            url = info['entries'][0]['url'] if 'entries' in info else info['url']
            title = info['entries'][0]['title'] if 'entries' in info else info['title']

        source = await discord.FFmpegOpusAudio.from_probe(url, **ffmpeg_options)
        ctx.voice_client.play(source, after=lambda e: print(f"Playback error: {e}") if e else None)
        await ctx.send(f"Now playing: {title}")

    except Exception as e:
        await ctx.send(f"Error playing track: {e}")
        print(f"Error: {e}")

@bot.command(name='stop')
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Playback stopped.")

# Replace with your bot token
bot.run('')
