import asyncio
import random
from aiogram import Bot, Dispatcher, html, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from flask import Flask
from threading import Thread

# 🚀 FREE DEPLOYMENT SERVER (Render par bot ko hamesha zinda rakhne ke liye)
app = Flask('')

@app.route('/')
def home():
    return "Casino Bot is Running Free!"

def run_server():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_server)
    t.daemon = True
    t.start()

BOT_TOKEN = "8628180136:AAFWY3LDxM01xIV4hr19JNOXWcnc7cEJ8iQ"
ADMINS = [7995159553]
TECH_SUPPORT_USER_ID = 7995159553
UPI_ID = "Shudhanshu539@slc"

# 📢 PRIVATE CHANNEL SETTINGS (Link aur verification ke liye)
INVITE_LINK = "https://t.me/+EZ9x8c8xBJdlYzhl"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

USER_BALANCES = {}

class DepositState(StatesGroup):
    waiting_for_amount = State()
    waiting_for_utr = State()

# 🔐 PRIVATE CHANNEL JOIN CHECKING FUNCTION
async def check_user_joined(user_id: int) -> bool:
    try:
        # Bot direct private links se check nahi kar sakta, jab tak woh khud admin na ho.
        # Hamein bot ko group me add karke admin banana zaroori hai.
        # Agar bot check nahi kar paa raha toh yeh automatic default return karega taaki code crash na ho.
        
        # Note: Aapko bot ko group me add karke admin banana hoga. 
        # Agar group ka ID pata chal jaye toh niche -100xxxxxxxx daal sakte hain. 
        # Abhi ke liye hum aapki di hui link par check lagane ki koshish kar rahe hain.
        chat_target = "-1002268715878" # Yeh simulation ID hai, bot admin hote hi active ho jayegi
        
        member = await bot.get_chat_member(chat_id=chat_target, user_id=user_id)
        if member.status in ["member", "administrator", "creator"]:
            return True
        return False
    except Exception:
        # Agar bot abhi tak admin nahi bana hai ya ID match nahi hui, toh backup validation:
        return False

def get_balance(user_id):
    if user_id not in USER_BALANCES:
        USER_BALANCES[user_id] = 0.0
    return USER_BALANCES[user_id]

def get_main_menu():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎰 Slots Game (₹50)", callback_query_data="game_slots")],
        [InlineKeyboardButton(text="🎲 Dice Even/Odd (₹30)", callback_query_data="game_dice")],
        [InlineKeyboardButton(text="💰 Balance Check", callback_query_data="view_balance")],
        [InlineKeyboardButton(text="📥 Deposit (UPI)", callback_query_data="deposit_upi"),
         InlineKeyboardButton(text="📤 Withdraw", callback_query_data="withdraw_money")]
    ])
    return keyboard

def get_join_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Join ZV VERSE BET", url=INVITE_LINK)],
        [InlineKeyboardButton(text="🔄 Check Joined / Start", callback_query_data="check_join_again")]
    ])
    return keyboard

@dp.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Check if user is admin (Admins bypass force join)
    if user_id in ADMINS:
        is_joined = True
    else:
        is_joined = await check_user_joined(user_id)
    
    if not is_joined and user_id not in ADMINS:
        await message.answer(
            text=f"⚠️ {html.bold('Access Denied!')}\n\nBot ko use karne ke liye aapko hamare official group/channel ko join karna zaroori hai. Niche diye button se join karein aur 'Check Joined' par click karein 👇",
            parse_mode="HTML",
            reply_markup=get_join_keyboard()
        )
        return

    user_name = message.from_user.full_name
    balance = get_balance(user_id)
    welcome_text = (
        f"👋 Welcome {html.bold(user_name)}!\n\n"
        f"🎰 {html.bold('ZV VERSE CASINO')}\n"
        f"💰 Balance: {html.bold('₹' + str(balance))}\n\n"
        f"Select a game below to play 👇"
    )
    await message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu())

@dp.callback_query(F.data == "check_join_again")
async def check_join_again(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if user_id in ADMINS:
        is_joined = True
    else:
        is_joined = await check_user_joined(user_id)
    
    if not is_joined and user_id not in ADMINS:
        await callback.answer("❌ Aapne abhi tak channel join nahi kiya hai!", show_alert=True)
        return
        
    await callback.message.delete()
    user_name = callback.from_user.full_name
    balance = get_balance(user_id)
    welcome_text = (
        f"🎉 Thanks for joining!\n\n"
        f"🎰 {html.bold('ZV VERSE CASINO')}\n"
        f"💰 Balance: {html.bold('₹' + str(balance))}\n\n"
        f"Select a game below to play 👇"
    )
    await callback.message.answer(welcome_text, parse_mode="HTML", reply_markup=get_main_menu())
    await callback.answer()

@dp.callback_query(F.data == "deposit_upi")
async def start_deposit(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="📥 Enter deposit amount (Numbers only, e.g., 100, 500):")
    await state.set_state(DepositState.waiting_for_amount)
    await callback.answer()

@dp.message(DepositState.waiting_for_amount)
async def process_amount(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("❌ Please enter a valid number:")
        return
    
    amount = int(message.text)
    await state.update_data(amount=amount)
    
    pay_text = (
        f"💳 {html.bold('UPI Payment Instructions')}\n\n"
        f"💵 Amount: {html.bold('₹' + str(amount))}\n"
        f"🆔 UPI ID: `{UPI_ID}`\n\n"
        f"⚠️ {html.bold('Steps:')}\n"
        f"1. Copy UPI ID and pay via PhonePe/GPay/Paytm.\n"
        f"2. Copy 12-digit UTR / Transaction ID.\n"
        f"3. Send UTR number here."
    )
    await message.answer(pay_text, parse_mode="HTML")
    await state.set_state(DepositState.waiting_for_utr)

@dp.message(DepositState.waiting_for_utr)
async def process_utr(message: Message, state: FSMContext):
    utr = message.text.strip()
    if len(utr) < 10:
        await message.answer("❌ Invalid UTR. Enter 12-digit UTR number:")
        return
        
    data = await state.get_data()
    amount = data['amount']
    user_id = message.from_user.id
    user_name = message.from_user.full_name
    
    admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Approve", callback_query_data=f"app_{user_id}_{amount}")],
        [InlineKeyboardButton(text="❌ Reject", callback_query_data=f"rej_{user_id}")]
    ])
    
    for admin in ADMINS:
        try:
            await bot.send_message(
                chat_id=admin,
                text=f"📢 **New Deposit Request**\n\n👤 User: {user_name} (ID: {user_id})\n💵 Amount: ₹{amount}\n🔑 UTR: `{utr}`",
                parse_mode="HTML",
                reply_markup=admin_keyboard
            )
        except Exception:
            pass
            
    await message.answer("⏳ Request sent to admin for verification.")
    await state.clear()

@dp.callback_query(F.data.startswith("app_"))
async def approve_deposit(callback: CallbackQuery):
    _, user_id, amount = callback.data.split("_")
    user_id = int(user_id)
    amount = int(amount)
    
    USER_BALANCES[user_id] = get_balance(user_id) + amount
    
    try:
        await bot.send_message(chat_id=user_id, text=f"🎉 Deposit of ₹{amount} approved!")
    except Exception:
        pass
        
    await callback.message.edit_text(text=callback.message.text + "\n\n✅ Approved")
    await callback.answer()

@dp.callback_query(F.data.startswith("rej_"))
async def reject_deposit(callback: CallbackQuery):
    _, user_id = callback.data.split("_")
    user_id = int(user_id)
    
    try:
        await bot.send_message(chat_id=user_id, text="❌ Deposit rejected.")
    except Exception:
        pass
        
    await callback.message.edit_text(text=callback.message.text + "\n\n❌ Rejected")
    await callback.answer()

@dp.callback_query(F.data == "view_balance")
async def callback_balance(callback: CallbackQuery):
    balance = get_balance(callback.from_user.id)
    await callback.message.edit_text(
        text=f"💰 Current Balance: {html.bold('₹' + str(balance))}",
        parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="🔙 Back", callback_query_data="main_menu")]])
    )
    await callback.answer()

@dp.callback_query(F.data == "main_menu")
async def callback_main_menu(callback: CallbackQuery):
    balance = get_balance(callback.from_user.id)
    welcome_text = (
        f"🎰 {html.bold('ZV VERSE CASINO')}\n"
        f"💰 Balance: {html.bold('₹' + str(balance))}\n\n"
        f"Select a game to play:"
    )
    await callback.message.edit_text(welcome_text, parse_mode="HTML", reply_markup=get_main_menu())
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
