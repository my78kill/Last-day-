from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def vote_keyboard(players, voter):

    buttons = []

    for uid,name in players.items():

        if uid != voter:

            buttons.append([
                InlineKeyboardButton(
                    text=name,
                    callback_data=f"vote_{uid}"
                )
            ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)