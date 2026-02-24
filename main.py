import asyncio
import wikipediaapi
import requests
import random
from os import getenv
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, Message, CallbackQuery

# 1. Sozlamalar
load_dotenv()
TOKEN = getenv("BOT_TOKEN")

# Wikipedia sozlamasi (User-agent va Til)
wiki_uz = wikipediaapi.Wikipedia(
    language='uz',
    extract_format=wikipediaapi.ExtractFormat.WIKI,
    user_agent="QalbGavhariBot/8.0 (admin@example.com)"
)

bot = Bot(token=TOKEN)
dp = Dispatcher()

# ===================== KENGAYTIRILGAN FAKTLAR BAZASI =====================
BIG_FACTS = [
    {
        "title": "🪐 Koinotning cheksizligi",
        "desc": "Kuzatilishi mumkin bo'lgan koinotda taxminan 2 trillionta galaktika mavjud. Har bir galaktikada esa o'rtacha 100 milliardan ortiq yulduz bor."
    },
    {
        "title": "🧠 Inson xotirasi",
        "desc": "Inson miyasining ma'lumot saqlash hajmi taxminan 2.5 petabaytga teng. Bu 300 yil davomida to'xtovsiz HD video yozib olishga yetadi."
    },
    {
        "title": "🐝 Tabiat muvozanati",
        "desc": "Agar asalarilar butunlay yo'q bo'lib ketsa, insoniyat oziq-ovqat tanqisligi tufayli bor-yo'g'i 4 yil yashay olishi mumkin."
    },
    {
        "title": "🌊 Mariana botig'i",
        "desc": "Okeanning eng chuqur nuqtasida bosim har kvadrat santimetrga 1 tonnadan oshadi. Bu xuddi bitta odamning ustiga 50 ta Boeing-747 samolyoti turgandek gap."
    }
]


# ===================== MENYULAR =====================

def main_menu():
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📚 Wikipedia (Qidiruv bo'limi)", callback_data="wiki_help"))
    builder.row(InlineKeyboardButton(text="💰 Valyuta (Markaziy Bank)", callback_data="curr_mode"))
    builder.row(InlineKeyboardButton(text="🧠 Tasodifiy Fakt", callback_data="fact_mode"))
    builder.row(InlineKeyboardButton(text="❌ Menyuni Yopish", callback_data="close_bot"))
    builder.adjust(1)
    return builder.as_markup()


def back_menu():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Asosiy Menyu", callback_data="main_home"))
    return builder.as_markup()


# ===================== HANDLERLAR =====================

@dp.message(CommandStart())
async def cmd_start(message: Message):
    welcome_text = (
        f"🌟 **Assalomu alaykum, {message.from_user.full_name}!**\n\n"
        "**'Qalb Gavhari'** intellektual tizimi to'liq ishga tushirildi.\n"
        "Barcha bo'limlar stabil va xatosiz ishlamoqda.\n\n"
        "💡 **Wikipedia:** Menga shunchaki biror so'z yozing.\n"
        "💡 **Valyuta:** Tugmani bosing va jonli kursni oling.\n"
        "💡 **Fakt:** Kutilmagan ilmiy ma'lumotlarni o'qing."
    )
    await message.answer(welcome_text, reply_markup=main_menu(), parse_mode="Markdown")


# 1. Valyuta Kursi (Xatosiz va alohida xabar)
@dp.callback_query(F.data == "curr_mode")
async def currency_info(callback: CallbackQuery):
    try:
        # Eng ishonchli CBU API manzili
        res = requests.get("https://cbu.uz/uz/arkhiv-kursov-valyut/json/").json()
        usd = next(i for i in res if i['Ccy'] == 'USD')
        eur = next(i for i in res if i['Ccy'] == 'EUR')

        text = (
            "💰 **RASMIY VALYUTA KURSLARI**\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"🇺🇸 **Dollar:** `{usd['Rate']}` so'm\n"
            f"🇪🇺 **Evro:** `{eur['Rate']}` so'm\n"
            "⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
            f"📅 _Oxirgi yangilanish: {usd['Date']}_"
        )
        await callback.message.answer(text, parse_mode="Markdown", reply_markup=main_menu())
        await callback.answer()
    except Exception as e:
        await callback.answer("⚠️ Valyuta tizimida texnik nosozlik!", show_alert=True)


# 2. Kengaytirilgan Fakt
@dp.callback_query(F.data == "fact_mode")
async def fact_info(callback: CallbackQuery):
    item = random.choice(BIG_FACTS)
    text = (
        f"💎 **{item['title']}**\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        f"{item['desc']}\n"
        f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
        "✨ _Yana bilish uchun tugmani bosing._"
    )
    await callback.message.answer(text, parse_mode="Markdown", reply_markup=main_menu())
    await callback.answer()


# 3. Wikipedia Yordamchi matni
@dp.callback_query(F.data == "wiki_help")
async def wiki_help(callback: CallbackQuery):
    await callback.answer("Menga shunchaki biror so'z yozib yuboring!", show_alert=True)


# 4. 🔥 AVTO-QIDIRUV (Hamma narsani Wikipedia'dan qidiradi)
@dp.message(F.text)
async def auto_search(message: Message):
    if message.text.startswith('/'): return

    wait_msg = await message.answer("🔍 *Qalb Gavhari qidirmoqda...*", parse_mode="Markdown")

    try:
        page = wiki_uz.page(message.text)
        if page.exists():
            # Maqolani kengroq olish (3500 belgi)
            content = page.text if len(page.text) < 3500 else page.text[:3500] + "..."
            res = (
                f"📖 **Mavzu: {page.title}**\n"
                f"⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯⎯\n"
                f"{content}\n\n"
                f"🔗 [Vikipediyada o'qish]({page.fullurl})"
            )
            await wait_msg.edit_text(res, parse_mode="Markdown", disable_web_page_preview=True)
        else:
            await wait_msg.edit_text(
                "😔 Afsuski, bu mavzuda ma'lumot topilmadi.\n"
                "Iltimos, so'zni to'g'ri yozganingizga ishonch hosil qiling.",
                reply_markup=main_menu()
            )
    except Exception:
        await wait_msg.edit_text("⚠️ Qidiruvda xatolik yuz berdi. Keyinroq urinib ko'ring.")


@dp.callback_query(F.data == "main_home")
async def go_home(callback: CallbackQuery):
    await callback.message.answer("Asosiy menyudasiz:", reply_markup=main_menu())
    await callback.answer()


@dp.callback_query(F.data == "close_bot")
async def close(callback: CallbackQuery):
    await callback.message.delete()


# ===================== ISHGA TUSHIRISH =====================
async def main():
    print("💎 Qalb Gavhari v8.0 FULL STABLE ishga tushdi...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

