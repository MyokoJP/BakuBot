import asyncio

import discord
from apscheduler.schedulers.background import BackgroundScheduler
from discord.ext import commands

import config
from utils import Database, VerifiedMember

bot = commands.Bot(intents=discord.Intents.all(), command_prefix=[])


@bot.event
async def on_ready():
    await load_extensions()
    # await bot.tree.sync()
    print(f"{bot.user} としてログインしました")

    # Database
    Database.initialize()

    # Status
    guilds = bot.guilds
    asyncio.create_task(switch_status(guilds))

    # Schedule
    scheduler = BackgroundScheduler()
    scheduler.add_job(VerifiedMember.refresh, "cron", hour=0)
    scheduler.start()


async def load_extensions():
    await bot.load_extension("commands.backup")
    await bot.load_extension("commands.verify")
    await bot.load_extension("commands.leave")
    await bot.load_extension("commands.roleset")
    await bot.load_extension("web")


async def switch_status(guilds):
    count = 0
    for i in guilds:
        count += i.member_count

    while True:
        await bot.change_presence(activity=discord.Game(name=f"{len(guilds)} サーバー | {count} メンバー"))
        await asyncio.sleep(5)
        await bot.change_presence(activity=discord.Game(name=f"By UTA SHOP"))
        await asyncio.sleep(5)


bot.run(config.TOKEN)
