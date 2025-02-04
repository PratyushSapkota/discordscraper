import discord
from dotenv import load_dotenv
from discordScraper import scrapeMessages
import asyncio
from seleniumFunctions import login, initializeDriver
from utils import clearScreenshotDirectory, initialize_last_message_file, store_message, get_last_message

load_dotenv()
import os

# RECIEVE_CHANNEL = "1333133280471548016"
RECIEVE_CHANNEL = "1247230290972377312"

TOKEN = os.getenv("TOKEN")
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
filter = "in: 📝︱feedback "
scrapeServerChannel = "1029781241702129716/1030196642508447785"


async def runScraper():
    driver, wait = initializeDriver(60)
    try:
        while True:
            messages = await scrapeMessages(
                driver=driver,
                wait=wait,
                scrapeServerChannel=scrapeServerChannel,
            )
            print(" **BOT** Found:", len(messages))
            if messages:
                messages.reverse()
                for idx, message in enumerate(messages):
                    print(idx)
                    await send_message(message)
            await asyncio.sleep(60)
            print("STARTING SCRAPE AGAIN")

    except Exception as e:
        print("ERROR in runScraper:", e)

    finally:
        print("_" * 150)
        print("Driver Shutdown")
        print("_" * 150)
        driver.close()
        driver.quit()


@client.event
async def on_ready():
    clearScreenshotDirectory()
    initialize_last_message_file()
    print(f"Bot is ready and logged in as {client.user}")
    asyncio.create_task(runScraper())


async def send_message(content):
    try:
        await client.get_channel(int(RECIEVE_CHANNEL)).send(content)
    except Exception as e:
        print(f"Discord exception: {e}")


client.run(TOKEN)
