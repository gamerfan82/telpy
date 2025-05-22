import json
import csv
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.types import ParseMode
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from keep_alive import keep_alive
keep_alive()

PROXY_URL = "http://proxy.server:3128"
bot = Bot(token="8021241750:AAEDJfbl2PdKplMz2rFVz7ACh1S1bFTcygs")
dp = Dispatcher(bot, storage=MemoryStorage())

CSV_FILE = "transactions.csv"
USER_NAMES = ["عرفان صادقی", "امیرحسین قلی نیا", "ابوالفضل محمدشاهی", "ماکان کریمیان", "ابوالفضل فرخ پور", "محمدرضا صمدی", "مهدی عباسی", "امین کاظمی"]
USERS_FILE = "users.json"

# تعریف کلاس وضعیت برای مراحل مختلف تراکنش
class TransactionForm(StatesGroup):
    sender = State()
    receiver = State()
    amount = State()
    subject = State()

class DeleteConfirm(StatesGroup):
    confirm = State()

delete_index = {}

def main_menu():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📄 مشاهده و حذف تراکنش ها", callback_data="show_report"),
        InlineKeyboardButton("➕ افزودن تراکنش", callback_data="add_transaction")
        )
    return kb

def load_users():
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_user(name, chat_id):
    users = load_users()
    users[name] = chat_id
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def build_name_keyboard(prefix: str):
    keyboard = InlineKeyboardMarkup(row_width=2)
    for name in USER_NAMES:
        keyboard.insert(InlineKeyboardButton(name, callback_data=f"{prefix}:{name}"))
    return keyboard

@dp.message_handler(commands=['transactions'])
async def show_transactions_in_group(message: types.Message):
    # فقط اجازه بده در گروه یا سوپرگروه اجرا بشه
    if message.chat.type not in ['group', 'supergroup']:
        await message.reply("❌ این دستور فقط در گروه‌ها قابل استفاده است.")
        return

    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))
            if not reader:
                await message.reply("⚠️ هنوز هیچ تراکنشی ثبت نشده.")
                return

            # تقسیم‌بندی پیام‌ها اگر زیاد بودن (هر پیام زیر 4096 کاراکتر)
            text = "📋 لیست تراکنش‌ها:\n"
            for i, row in enumerate(reader):
                text += f"{i+1}. {row['فرستنده']} → {row['گیرنده']} ({row['مبلغ']} تومان) - {row['موضوع']}\n"

            if len(text) > 4000:
                # تقسیم به چند بخش
                parts = [text[i:i+4000] for i in range(0, len(text), 4000)]
                for part in parts:
                    await message.answer(part)
            else:
                await message.reply(text)
    except Exception as e:
        await message.reply(f"❌ خطا در نمایش تراکنش‌ها: {e}")



@dp.message_handler(commands=['start'])
async def welcome(message: types.Message):
    kb = InlineKeyboardMarkup()
    for name in USER_NAMES:
        kb.add(InlineKeyboardButton(name, callback_data=f"register:{name}"))
    await message.answer("سلام! لطفاً اسم خودت رو انتخاب کن تا ربات بتونه بهت پیام خصوصی بده:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("register:"))
async def register_user(call: types.CallbackQuery):
    name = call.data.split(":")[1]
    save_user(name, call.from_user.id)
    await call.message.edit_text(f"✅ خوش اومدی {name}!\nاز منوی زیر استفاده کن:", reply_markup=main_menu())
    await call.answer()

@dp.callback_query_handler(lambda c: c.data == "add_transaction")
async def start_transaction(call: types.CallbackQuery):
    await call.message.answer("👤 فرستنده پول را انتخاب کن:", reply_markup=build_name_keyboard("sender"))
    await TransactionForm.sender.set()
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("sender:"), state=TransactionForm.sender)
async def sender_selected(call: types.CallbackQuery, state: FSMContext):
    sender = call.data.split(":")[1]
    await state.update_data(sender=sender)
    await call.message.edit_text(f"✅ فرستنده انتخاب شد: {sender}")
    await call.message.answer("👤 گیرنده پول را انتخاب کن:", reply_markup=build_name_keyboard("receiver"))
    await TransactionForm.receiver.set()
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("receiver:"), state=TransactionForm.receiver)
async def receiver_selected(call: types.CallbackQuery, state: FSMContext):
    receiver = call.data.split(":")[1]
    await state.update_data(receiver=receiver)
    await call.message.edit_text(f"✅ گیرنده انتخاب شد: {receiver}")
    await call.message.answer("💵 مبلغ را به تومان وارد کن:")
    await TransactionForm.amount.set()
    await call.answer()

@dp.message_handler(state=TransactionForm.amount)
async def amount_received(message: types.Message, state: FSMContext):
    amount = message.text
    await state.update_data(amount=amount)
    await message.answer("📝 موضوع تراکنش را وارد کن:")
    await TransactionForm.subject.set()

@dp.message_handler(state=TransactionForm.subject)
async def subject_received(message: types.Message, state: FSMContext):
    subject = message.text
    data = await state.get_data()
    sender = data['sender']
    receiver = data['receiver']
    amount = data['amount']

    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['فرستنده', 'گیرنده', 'مبلغ', 'موضوع']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        csvfile.seek(0, 2)
        if csvfile.tell() == 0:
            writer.writeheader()
        writer.writerow({'فرستنده': sender, 'گیرنده': receiver, 'مبلغ': amount, 'موضوع': subject})

    users = load_users()
    if receiver in users:
        try:
            await bot.send_message(
                users[receiver],
                f"📥 تراکنش جدید:\n{sender} باید برای تو {amount} تومان ارسال کنه.\nموضوع: {subject}"
            )
        except Exception as e:
            print(f"خطا در ارسال پیام به {receiver}: {e}")

    await state.finish()
    await message.answer("✅ تراکنش با موفقیت ثبت شد.", reply_markup=main_menu())

@dp.callback_query_handler(lambda c: c.data == "show_report")
async def show_report(call: types.CallbackQuery):
    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))
            if not reader:
                await call.message.answer("⚠️ تراکنشی برای نمایش وجود ندارد.")
                return

            kb = InlineKeyboardMarkup(row_width=1)
            for i, row in enumerate(reader):
                sender = row['فرستنده']
                receiver = row['گیرنده']
                amount = row['مبلغ']
                subject = row['موضوع']
                btn_text = f"{i+1}. {sender} --> {receiver} ({amount}) - {subject}"
                kb.add(InlineKeyboardButton(btn_text, callback_data=f"remove:{i}"))

            await call.message.answer("📝 گزارش تراکنش‌ها:\nبرای حذف روی تراکنش ها کلیک کنید", reply_markup=kb)
    except Exception as e:
        await call.message.answer(f"❌ خطا در نمایش تراکنش‌ها: {e}")
    await call.answer()

@dp.callback_query_handler(lambda c: c.data.startswith("remove:"))
async def remove_transaction(call: types.CallbackQuery, state: FSMContext):
    index = int(call.data.split(":")[1])
    delete_index[call.from_user.id] = index
    await call.message.answer("برای حذف تراکنش، لطفاً عبارت \"حذف\" را ارسال کن:")
    await DeleteConfirm.confirm.set()
    await call.answer()

@dp.message_handler(state=DeleteConfirm.confirm)
async def confirm_deletion(message: types.Message, state: FSMContext):
    if message.text.strip() != "حذف":
        await message.answer("❌ حذف لغو شد. برای حذف باید دقیقاً عبارت \"حذف\" را وارد کنی.")
        await state.finish()
        return

    index = delete_index.get(message.from_user.id)
    try:
        with open(CSV_FILE, newline='', encoding='utf-8') as csvfile:
            reader = list(csv.DictReader(csvfile))

        if 0 <= index < len(reader):
            removed = reader.pop(index)

            with open(CSV_FILE, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['فرستنده', 'گیرنده', 'مبلغ', 'موضوع']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for row in reader:
                    writer.writerow(row)

            await message.answer(f"✅ تراکنش حذف شد:\n{removed['فرستنده']} --> {removed['گیرنده']} ({removed['مبلغ']}) - {removed['موضوع']}", reply_markup=main_menu())
        else:
            await message.answer("❗ تراکنش موردنظر پیدا نشد.")
    except Exception as e:
        await message.answer(f"❌ خطا در حذف تراکنش: {e}")
    await state.finish()
if __name__ == '__main__':
    executor.start_polling(dp)

