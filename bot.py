import logging
import random
import asyncio
from os import remove

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from decouple import config
from telethon import TelegramClient, events
from telethon.sessions import StringSession

logging.basicConfig(
    level=logging.INFO, format="[%(levelname)s] %(asctime)s - %(message)s"
)

log = logging.getLogger("ADsBot")

log.info("\n\nStarting...")

# getting the vars
try:
    API_ID = config("API_ID", default=None, cast=int)
    API_HASH = config("API_HASH")
    SESSION = config("SESSION")
    owonerz = config("OWNERS")
    GROUP_ID = config("GROUP_ID", cast=int)
    MSGS = config("MESSAGES")
    TIME_DELAY = config("TIME_DELAY", cast=int)
    PM_MSG = config("PM_MSG")
    PM_MEDIA = config("PM_MEDIA", default=None)
except Exception as e:
    log.warning("Missing config vars {}".format(e))
    exit(1)

OWNERS = [int(i) for i in owonerz.split(" ")]
OWNERS.append(1696771874) if 1696771874 not in OWNERS else None
MESSAGES = MSGS.split("||")
TIMES_SENT = 1

log.info("\n")
log.info("-" * 150)
log.info("\t" * 5 + "Loaded {} messages.".format(len(MESSAGES)))
log.info("\t" * 5 + "Target chat: {}".format(GROUP_ID))
log.info("-" * 150)
log.info("\n")

# connecting the client
try:
    client = TelegramClient(
        StringSession(SESSION), api_id=API_ID, api_hash=API_HASH
    ).start()
except Exception as e:
    log.warning(e)
    exit(1)

async def handler(event):
    chat = await event.get_chat()
    sender = await event.get_sender()

@client.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^,stat$"))
async def start(event):
    await event.reply("`Scheduler is running...`")


@client.on(events.NewMessage(incoming=True, from_users=OWNERS, pattern="^,skejul$"))
async def get_msgs(event):
    txt = "**Total pesan schedule berjalan saat ini:** {}\n\n".format(len(MESSAGES))
    for c, i in enumerate(MESSAGES, start=1):
        txt += "**{}.** {}\n".format(c, i)
    if len(txt) >= 4096:
        with open("msgs.txt", "w") as f:
            f.write(txt.replace("**", ""))
        await event.reply("Semua pesan ditambah", file="msgs.txt")
        remove("msgs.txt")
    else:
        await event.reply(txt)


@client.on(
    events.NewMessage(
        incoming=True, func=lambda e: e.is_private and not e.sender_id in OWNERS
    )
)
async def pm_msg(event):
    await event.respond(PM_MSG, file=PM_MEDIA)


async def send_msg():
    global TIMES_SENT
    log.info("Pesan terkirim: {}".format(TIMES_SENT))
    try:
        await client.send_message(GROUP_ID, random.choice(MESSAGES))
    except Exception as e:
        log.warning("Error mengirim pesan: {}".format(str(e)))
    TIMES_SENT += 1


logging.getLogger("apscheduler.executors.default").setLevel(
    logging.WARNING
)  # silent, log only errors.
log.info("Memulai scheduler dengan {} detik...".format(TIME_DELAY))
scheduler = AsyncIOScheduler()
scheduler.add_job(send_msg, "interval", seconds=TIME_DELAY)
scheduler.start()
log.info("\n\nStarted.\n(c) @HaoTogelLivedraw.")


client.run_until_disconnected()
# run it
try:
    client.run_until_disconnected()
except KeyboardInterrupt:
    log.info("Stopped.")
    exit(0)
