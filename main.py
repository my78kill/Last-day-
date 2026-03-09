import asyncio
import threading
import os

from flask import Flask

from aiogram import Bot, Dispatcher
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command

from config import BOT_TOKEN, NIGHT_DURATION, DAY_DURATION
from game_manager import GameSession
from keyboards import vote_keyboard
from keep_alive import keep_alive

keep_alive()

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

games = {}

# ---------------- FLASK SERVER ----------------

app = Flask(__name__)

@app.route("/")
def home():
    return "Virus Outbreak Bot is running!"

# ---------------- BOT COMMANDS ----------------

@dp.message(Command("start"))
async def bot_start(message: Message):

    welcome_text = """
🧬 Welcome to **Virus Outbreak**!

A deadly virus has spread through the city…
Some players are secretly infected 🦠 while others are trying to survive 🛡.

Your mission depends on your role.

👥 **Multiplayer Social Deduction Game**

━━━━━━━━━━━━━━

🎮 **How to Play**

1️⃣ Add this bot to a **group**
2️⃣ Players join using **/join**
3️⃣ Minimum **8 players required**
4️⃣ Maximum **25 players allowed**
5️⃣ Host starts the game with **/startgame**

🌙 At night special roles perform actions  
☀ During the day players discuss and vote  

⚠ Voting and actions happen **privately in bot DM**

━━━━━━━━━━━━━━

🏆 **Win Conditions**

🛡 Survivors → eliminate all infected  
🦠 Virus Team → outnumber survivors  
⚖ Neutral roles → complete their own objective  

━━━━━━━━━━━━━━

Type **/help** to see full rules.

Good luck surviving the outbreak… 🧬
"""

    await message.answer(welcome_text)


@dp.message(Command("help"))
async def help_cmd(message: Message):

    text = """
🧬 **Virus Outbreak - Help**

🎮 **Game Commands**

/join → Join the game lobby  
/startgame → Start the match (min 8 players)

━━━━━━━━━━━━━━

🌙 **Night Phase**
Special roles secretly perform actions.

☀ **Day Phase**
Players discuss and vote to eliminate someone.

━━━━━━━━━━━━━━

🗳 **Voting**
During the day you will receive a **private message**
with buttons to vote for a player.

━━━━━━━━━━━━━━

🏆 **Win Conditions**

🦠 Virus Team → outnumber survivors  
🛡 Survivors → eliminate all infected

━━━━━━━━━━━━━━

⚠ Make sure to **start the bot in DM**
otherwise you won't receive role messages.
"""

    await message.answer(text)


@dp.message(Command("join"))
async def join(message: Message):

    chat = message.chat.id
    user = message.from_user.id
    name = message.from_user.first_name

    if chat not in games:
        games[chat] = GameSession(chat)

    game = games[chat]

    if game.add_player(user, name):
        await message.reply(f"{name} joined the game")
    else:
        await message.reply("Already joined")


@dp.message(Command("startgame"))
async def start_game(message: Message):

    chat = message.chat.id
    game = games.get(chat)

    if not game:
        return

    if len(game.players) < 8:
        await message.reply("Need at least 8 players")
        return

    game.distribute_roles()

    for uid in game.players:

        role = game.roles[uid]

        try:
            await bot.send_message(uid, f"Your role: {role}")
        except:
            pass

    await message.answer("🌙 Night begins")

    await asyncio.sleep(NIGHT_DURATION)

    await day_phase(chat)


async def day_phase(chat):

    game = games[chat]

    players = {
        uid: name for uid, name in game.players.items()
        if uid in game.alive
    }

    for uid in players:

        try:
            await bot.send_message(
                uid,
                "Vote a player",
                reply_markup=vote_keyboard(players, uid)
            )
        except:
            pass

    await asyncio.sleep(DAY_DURATION)

    eliminated = game.resolve_votes()

    if eliminated:
        await bot.send_message(chat, f"💀 {game.players[eliminated]} eliminated")

    win = game.check_win()

    if win:

        await bot.send_message(chat, f"🏆 {win} win!")

        del games[chat]

    else:

        await bot.send_message(chat, "Next round begins")

        await asyncio.sleep(5)

        await day_phase(chat)


@dp.callback_query()
async def vote_handler(call: CallbackQuery):

    chat = call.message.chat.id
    user = call.from_user.id

    game = games.get(chat)

    if not game:
        return

    if call.data.startswith("vote_"):

        target = int(call.data.split("_")[1])

        game.vote(user, target)

        await call.answer("Vote counted")


# ---------------- BOT RUNNER ----------------

async def start_bot():
    await dp.start_polling(bot)

def run_bot():
    asyncio.run(start_bot())


# ---------------- MAIN ----------------

if __name__ == "__main__":

    # run bot in thread
    bot_thread = threading.Thread(target=run_bot)
    bot_thread.start()

    # run flask server
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
