import os
import logging

BOT_TOKEN = os.getenv("BOT_TOKEN")

MIN_PLAYERS = 8
MAX_PLAYERS = 25

NIGHT_DURATION = 45
DAY_DURATION = 90

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)