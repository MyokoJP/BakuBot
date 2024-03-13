import asyncio

import discord
from apscheduler.schedulers.background import BackgroundScheduler
from discord.ext import commands, tasks

import config
from utils import Database, VerifiedMember

bot = commands.Bot(intents=discord.Intents.all(), command_prefix=[])


@bot.event
async def on_ready():
    await load_extensions()
    await bot.tree.sync()
    print(f"{bot.user} としてログインしました")

    # Database
    Database.initialize()

    # Task
    switch_status.start()


async def load_extensions():
    await bot.load_extension("commands.backup")
    await bot.load_extension("commands.verify")
    await bot.load_extension("commands.leave")
    await bot.load_extension("commands.roleset")
    await bot.load_extension("web")


playing = 0


@tasks.loop(seconds=10)
async def switch_status():
    global playing

    if playing == 0:
        count = 0
        for i in bot.guilds:
            count += i.member_count

        await bot.change_presence(
            activity=discord.Game(name=f"{len(bot.guilds)} サーバー | {count} メンバー"))
        playing = 1
    else:
        await bot.change_presence(activity=discord.Game(name=f"By UTA SHOP"))
        playing = 0


bot.run(config.TOKEN)
