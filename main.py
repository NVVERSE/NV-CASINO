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

# -------------------------------------------------------------
# 1. FLASK WEB SERVER (Render Port Binding & Health Check)
# -------------------------------------------------------------
app = Flask("")


@app.route("/")
def home():
    return "ZV Verse Casino Engine: Active & Online"


def run_server():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)


def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()


# -------------------------------------------------------------
# 2. CONFIGURATION & SETUP
# -------------------------------------------------------------
BOT_TOKEN = "8728557922:AAH2GqE6nqtF1Mm_-GT5Fq6T5I2r5CykHic"
ADMIN_ID = 7995159553
UPI_ID = "Shudhanshu539@slc"  # Aapki UPI ID Yahan Hai

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


# -------------------------------------------------------------
# 3. MAIN MENU KEYBOARD (16 GAMES + DEPOSIT)
# -------------------------------------------------------------
def get_main_menu():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="👋 Rock Paper Scissors", callback_query_data="g_rps"
                ),
                InlineKeyboardButton(
                    text="🤑 Coin Flip", callback_query_data="g_cf"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="💕 Dice", callback_query_data="g_dice"
                ),
                InlineKeyboardButton(
                    text="😳 Darts", callback_query_data="g_darts"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏀 Basketball", callback_query_data="g_basket"
                ),
                InlineKeyboardButton(
                    text="⚽️ Football", callback_query_data="g_foot"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="6️⃣ Bowling", callback_query_data="g_bowl"
                ),
                InlineKeyboardButton(
                    text="🎰 Slots", callback_query_data="g_slots"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🏰 Towers", callback_query_data="g_towers"
                ),
                InlineKeyboardButton(
                    text="🚀 Limbo", callback_query_data="g_limbo"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🎲 Dice Rush", callback_query_data="g_dr"
                ),
                InlineKeyboardButton(
                    text="🎲 7Up Down", callback_query_data="g_7up"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🃏 BlackJack", callback_query_data="g_bj"
                ),
                InlineKeyboardButton(
                    text="💣 Mines", callback_query_data="g_mines"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="🔒 Vault", callback_query_data="g_vault"
                ),
                InlineKeyboardButton(
                    text="🏏 Cricket", callback_query_data="g_cricket"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="📥 Deposit (UPI)", callback_query_data="deposit_upi"
                ),
                InlineKeyboardButton(
                    text="💰 Check Balance", callback_query_data="view_bal"
                ),
            ],
        ]
    )


# -------------------------------------------------------------
# 4. COMMAND & CALLBACK HANDLERS
# -------------------------------------------------------------
@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    bal = get_balance(user_id)

    admin_tag = (
        f"\n⚡ {html.bold('Admin Privileges Granted')}"
        if user_id == ADMIN_ID
        else ""
    )

    text = (
        f"👋 Welcome {html.bold(user_name)}!{admin_tag}\n\n"
        f"🎰 {html.bold('ZV VERSE CASINO')}\n"
        f"💰 Balance: {html.bold('₹' + str(bal))}\n\n"
        f"🤍 {html.bold('AVAILABLE GAMES')}\n"
        f"Select any game below to start playing 👇"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu())


# --- DEPOSIT FLOW ---
@dp.callback_query(F.data == "deposit_upi")
async def start_deposit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text="📥 Enter deposit amount in ₹ (Numbers only, e.g., 100, 500):",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Cancel", callback_query_data="main_menu"
                    )
                ]
            ]
        ),
    )
    await state.set_state(DepositState.waiting_for_amount)
    await callback.answer()


@dp.message(DepositState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number (e.g. 100):")
        return

    amount = int(message.text)
    await state.update_data(amount=amount)

    pay_text = (
        f"💳 {html.bold('UPI PAYMENT DETAILS')}\n\n"
        f"💵 Amount: {html.bold('₹' + str(amount))}\n"
        f"🆔 UPI ID: `{UPI_ID}`\n\n"
        f"⚠️ {html.bold('Instructions:')}\n"
        f"1. Pay ₹{amount} on above UPI ID.\n"
        f"2. Copy the 12-digit UTR / Transaction ID.\n"
        f"3. Send the UTR number here in chat."
    )
    await message.answer(pay_text, parse_mode="HTML")
    await state.set_state(DepositState.waiting_for_utr)


@dp.message(DepositState.waiting_for_utr)
async def process_utr(message: Message, state: FSMContext):
    utr = message.text.strip()
    if len(utr) < 8:
        await message.answer(
            "❌ Invalid UTR. Please enter valid Transaction ID / UTR:"
        )
        return

    data = await state.get_data()
    amount = data["amount"]
    user_id = message.from_user.id
    user_name = message.from_user.full_name

    admin_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="✅ Approve",
                    callback_query_data=f"app_{user_id}_{amount}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="❌ Reject", callback_query_data=f"rej_{user_id}"
                )
            ],
        ]
    )

    try:
        await bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📢 {html.bold('NEW DEPOSIT REQUEST')}\n\n👤 User: {user_name} (`{user_id}`)\n💵 Amount: ₹{amount}\n🔑 UTR: `{utr}`",
            parse_mode="HTML",
            reply_markup=admin_keyboard,
        )
    except Exception:
        pass

    await message.answer(
        "⏳ Deposit request sent to Admin! Your balance will update soon after verification."
    )
    await state.clear()


@dp.callback_query(F.data.startswith("app_"))
async def approve_deposit(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Only Admin can perform this action!")
        return

    _, user_id, amount = callback.data.split("_")
    user_id = int(user_id)
    amount = int(amount)

    USER_BALANCES[user_id] = get_balance(user_id) + amount

    try:
        await bot.send_message(
            chat_id=user_id,
            text=f"🎉 {html.bold('Deposit Approved!')}\n₹{amount} added to your account balance.",
            parse_mode="HTML",
        )
    except Exception:
        pass

    await callback.message.edit_text(
        text=callback.message.text + "\n\n✅ APPROVED BY ADMIN"
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("rej_"))
async def reject_deposit(callback: CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Only Admin can perform this action!")
        return

    _, user_id = callback.data.split("_")
    user_id = int(user_id)

    try:
        await bot.send_message(
            chat_id=user_id,
            text="❌ Your deposit request was rejected by Admin.",
        )
    except Exception:
        pass

    await callback.message.edit_text(
        text=callback.message.text + "\n\n❌ REJECTED BY ADMIN"
    )
    await callback.answer()


# --- GENERAL HANDLERS ---
@dp.callback_query(F.data == "view_bal")
async def process_bal(callback: CallbackQuery):
    bal = get_balance(callback.from_user.id)
    await callback.answer(f"Current Balance: ₹{bal}", show_alert=True)


@dp.callback_query(F.data == "main_menu")
async def process_menu(callback: CallbackQuery):
    bal = get_balance(callback.from_user.id)
    text = (
        f"🎰 {html.bold('ZV VERSE CASINO')}\n"
        f"💰 Balance: {html.bold('₹' + str(bal))}\n\n"
        f"Select an option below 👇"
    )
    await callback.message.edit_text(
        text, parse_mode="HTML", reply_markup=get_main_menu()
    )
    await callback.answer()


ANIMATED_GAMES = {
    "g_dice": "🎲",
    "g_darts": "🎯",
    "g_basket": "🏀",
    "g_foot": "⚽",
    "g_bowl": "🎳",
    "g_slots": "🎰",
}


@dp.callback_query(F.data.in_(ANIMATED_GAMES.keys()))
async def handle_animated_games(callback: CallbackQuery):
    emoji = ANIMATED_GAMES[callback.data]
    chat_id = callback.message.chat.id

    await callback.answer("Rolling...")
    msg = await bot.send_dice(chat_id=chat_id, emoji=emoji)

    await asyncio.sleep(2.5)
    await bot.send_message(
        chat_id=chat_id,
        text=f"Score: {msg.dice.value}!",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔄 Play Again", callback_query_data=callback.data
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="🔙 Main Menu", callback_query_data="main_menu"
                    )
                ],
            ]
        ),
    )


@dp.callback_query(F.data.startswith("g_"))
async def handle_custom_games(callback: CallbackQuery):
    game_code = callback.data.replace("g_", "").upper()
    await callback.message.edit_text(
        text=f"🎮 {html.bold(game_code + ' GAME')}\n\nInteractive game UI logic...",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Main Menu", callback_query_data="main_menu"
                    )
                ]
            ]
        ),
    )
    await callback.answer()


# -------------------------------------------------------------
# 5. EXECUTION & CLEANUP
# -------------------------------------------------------------
async def main():
    keep_alive()
    await bot.delete_webhook(drop_pending_updates=True)
    await asyncio.sleep(1)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
