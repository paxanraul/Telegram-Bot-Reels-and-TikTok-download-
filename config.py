import os

from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set")

IG_USERNAME = os.getenv("IG_USERNAME")
IG_SESSIONFILE = os.getenv("IG_SESSIONFILE")
ADMIN_ID = os.getenv("ADMIN_ID")
ADMIN_IDS = {
    value.strip()
    for value in os.getenv("ADMIN_IDS", "").split(",")
    if value.strip()
}
if ADMIN_ID:
    ADMIN_IDS.add(str(ADMIN_ID))


def is_admin(user_id: int) -> bool:
    return str(user_id) in ADMIN_IDS
