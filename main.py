import asyncio
import os
import random
from threading import Thread

from aiogram import Bot, Dispatcher, F, html
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from flask import Flask

# 🚀 Render Server Health Check
app = Flask("")


@app.route("/")
def home():
    return "Casino Bot Status: Active & Running"


def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()


# 🔑 Fresh Token
BOT_TOKEN = "8628180136:AAHOOjfNX5ZMrsSIktPis1yIm2vO4ErjyxE"
ADMINS = [7995159553]
UPI_ID = "Shudhanshu539@slc"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_BALANCES = {}


class DepositState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_utr = State()


def get_balance(user_id):
    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 0.0
    return USER_BALANCES[user_id]


def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🎰 Slots Game (₹50)", callback_query_data="game_slots"
                )
            ],
            [
                InlineKeyboardButton(
                    text="💰 Balance Check", callback_query_data="view_balance"
                )
            ],
            [
                InlineKeyboardButton(
                    text="📥 Deposit (UPI)", callback_query_data="deposit_upi"
                ),
                InlineKeyboardButton(
                    text="📤 Withdraw", callback_query_data="withdraw_money"
                ),
            ],
        ]
    )


@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    balance = get_balance(user_id)

    welcome_text = (
        f"👋 Welcome {html.bold(user_name)}!\n\n"
        f"🎰 {html.bold('ZV VERSE CASINO')}\n"
        f"💰 Balance: {html.bold('₹' + str(balance))}\n\n"
        f"Select an option below 👇"
    )
    await message.answer(
        welcome_text, parse_mode="HTML", reply_markup=get_main_menu()
    )


@dp.callback_query(F.data == "view_balance")
async def callback_balance(callback: CallbackQuery):
    balance = get_balance(callback.from_user.id)
    await callback.message.edit_text(
        text=f"💰 Current Balance: {html.bold('₹' + str(balance))}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Back", callback_query_data="main_menu"
                    )
                ]
            ]
        ),
    )
    await callback.answer()


@dp.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    balance = get_balance(callback.from_user.id)
    welcome_text = (
        f"🎰 {html.bold('ZV VERSE CASINO')}\n"
        f"💰 Balance: {html.bold('₹' + str(balance))}\n\n"
        f"Select an option below 👇"
    )
    await callback.message.edit_text(
        welcome_text, parse_mode="HTML", reply_markup=get_main_menu()
    )
    await callback.answer()


@dp.callback_query(F.data == "game_slots")
async def play_slots(callback: CallbackQuery):
    user_id = callback.from_user.id
    balance = get_balance(user_id)
    bet = 50

    if balance < bet:
        await callback.answer("❌ Insufficient balance!", show_alert=True)
        return

    USER_BALANCES[user_id] -= bet
    emojis = ["🍎", "🍋", "🍒", "💎", "7️⃣"]
    reel1, reel2, reel3 = random.choices(emojis, k=3)

    result_text = f"🎰 Rolling...\n\n[ {reel1} | {reel2} | {reel3} ]\n\n"

    if reel1 == reel2 == reel3:
        win = bet * 5
        USER_BALANCES[user_id] += win
        result_text += f"🎉 Jackpot! Won {html.bold('₹' + str(win))}!"
    elif reel1 == reel2 or reel2 == reel3 or reel1 == reel3:
        win = bet * 2
        USER_BALANCES[user_id] += win
        result_text += f"💵 Nice! Won {html.bold('₹' + str(win))}."
    else:
        result_text += "😢 No match. Try again!"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="🔄 Spin Again (₹50)", callback_query_data="game_slots"
                )
            ],
            [
                InlineKeyboardButton(
                    text="🔙 Back to Menu", callback_query_data="main_menu"
                )
            ],
        ]
    )
    await callback.message.edit_text(
        text=result_text, parse_mode="HTML", reply_markup=keyboard
    )
    await callback.answer()


async def main():
    keep_alive()
    # Puraane webhooks clear kar rahe hain taaki naya token instantly start ho sake
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(1)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
